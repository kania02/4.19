import sys,re,os,shutil
R=sys.argv[1]+'/drivers/misc/mediatek/'
def rep(f,old,new,cnt=1):
    p=R+f; s=open(p).read()
    if new in s and old not in s: return
    assert s.count(old)==cnt,(f,old[:40],s.count(old))
    open(p,'w').write(s.replace(old,new))
def after_last_include(f,block,anchor=None):
    p=R+f; s=open(p).read()
    if block.strip().splitlines()[0] in s: return
    ms=[m for m in re.finditer(r'^#include .*\n',s,re.M) if anchor is None or anchor in m.group(0)]
    m=ms[-1]
    open(p,'w').write(s[:m.end()]+block+s[m.end():])
# ---- ccmni
rep('ccmni/ccmni.c','\tvoid *accel_priv, select_queue_fallback_t fallback)','\tstruct net_device *sb_dev, select_queue_fallback_t fallback)')
rep('ccmni/ccmni.c','static void ccmni_napi_poll_timeout(unsigned long data)\n{\n\tstruct ccmni_instance *ccmni = (struct ccmni_instance *)data;\n',
'static void ccmni_napi_poll_timeout(struct timer_list *t)\n{\n\tstruct ccmni_timer_wrap *w = from_timer(w, t, t);\n\tstruct ccmni_instance *ccmni = w->ccmni;\n')
rep('ccmni/ccmni.c','\tccmni->timer = kzalloc(sizeof(struct timer_list), GFP_KERNEL);','\tccmni->timer = kzalloc(sizeof(struct ccmni_timer_wrap), GFP_KERNEL);')
rep('ccmni/ccmni.c','\t\tinit_timer(ccmni->timer);\n\t\tccmni->timer->function = ccmni_napi_poll_timeout;\n\t\tccmni->timer->data = (unsigned long)ccmni;\n',
'\t\t((struct ccmni_timer_wrap *)ccmni->timer)->ccmni = ccmni;\n\t\ttimer_setup(ccmni->timer, ccmni_napi_poll_timeout, 0);\n')
rep('ccmni/ccmni.c','if (!list_empty(&ccmni->napi->gro_list)) {','if (ccmni->napi->gro_bitmask) {')
after_last_include('ccmni/ccmni.c','''
#ifndef ARPHRD_PUREIP
#define ARPHRD_PUREIP 520
#endif
struct ccmni_timer_wrap {
	struct timer_list t;
	struct ccmni_instance *ccmni;
};
static void ccmni_netif_rx_list(struct list_head *head)
{
	struct sk_buff *skb, *next;

	list_for_each_entry_safe(skb, next, head, list) {
		list_del(&skb->list);
		netif_rx_ni(skb);
	}
}
#define netif_rx_list_ni ccmni_netif_rx_list
''')
# ---- eccci timers
after_last_include('eccci/hif/ccci_hif_cldma.c','''
void md_cd_traffic_monitor_func(unsigned long data);
static void cldma_timeout_timer_func(unsigned long data);
static void md_cd_traffic_timer_cb(struct timer_list *t)
{
	struct md_cd_ctrl *c = from_timer(c, t, traffic_monitor);

	md_cd_traffic_monitor_func((unsigned long)c);
}
static void cldma_timeout_timer_cb(struct timer_list *t)
{
	struct md_cd_queue *q = from_timer(q, t, timeout_timer);

	cldma_timeout_timer_func((unsigned long)q);
}
''','"ccci_port.h"')
rep('eccci/hif/ccci_hif_cldma.c','\tinit_timer(&queue->timeout_timer);\n\tqueue->timeout_timer.function = cldma_timeout_timer_func;\n\tqueue->timeout_timer.data = (unsigned long)queue;\n','\ttimer_setup(&queue->timeout_timer, cldma_timeout_timer_cb, 0);\n')
rep('eccci/hif/ccci_hif_cldma.c','\tinit_timer(&md_ctrl->traffic_monitor);\n\tmd_ctrl->traffic_monitor.function =\n\t\tmd_cd_traffic_monitor_func;\n\tmd_ctrl->traffic_monitor.data = (unsigned long)md_ctrl;\n','\ttimer_setup(&md_ctrl->traffic_monitor, md_cd_traffic_timer_cb, 0);\n')
after_last_include('eccci/hif/ccci_hif_ccif.c','''
static void md_ccif_traffic_monitor_func(unsigned long data);
static void md_ccif_traffic_timer_cb(struct timer_list *t)
{
	struct md_ccif_ctrl *c = from_timer(c, t, traffic_monitor);

	md_ccif_traffic_monitor_func((unsigned long)c);
}
''')
rep('eccci/hif/ccci_hif_ccif.c','\tinit_timer(&md_ctrl->traffic_monitor);\n\tmd_ctrl->traffic_monitor.function = md_ccif_traffic_monitor_func;\n\tmd_ctrl->traffic_monitor.data = (unsigned long)md_ctrl;\n','\ttimer_setup(&md_ctrl->traffic_monitor, md_ccif_traffic_timer_cb, 0);\n')
after_last_include('eccci/hif/ccci_hif_dpmaif.c','''
static void dpmaif_traffic_monitor_func(unsigned long data);
static void dpmaif_traffic_timer_cb(struct timer_list *t)
{
	struct hif_dpmaif_ctrl *c = from_timer(c, t, traffic_monitor);

	dpmaif_traffic_monitor_func((unsigned long)c);
}
''','ccci_hif_dpmaif.h')
rep('eccci/hif/ccci_hif_dpmaif.c','\tinit_timer(&hif_ctrl->traffic_monitor);\n\thif_ctrl->traffic_monitor.function = dpmaif_traffic_monitor_func;\n\thif_ctrl->traffic_monitor.data = (unsigned long)hif_ctrl;\n','\ttimer_setup(&hif_ctrl->traffic_monitor, dpmaif_traffic_timer_cb, 0);\n')
# ---- part2
rep('eccci/hif/ccci_hif_cldma.c','static void cldma_timeout_timer_func(unsigned long data);\nstatic void md_cd_traffic_timer_cb','#ifdef ENABLE_CLDMA_TIMER\nstatic void cldma_timeout_timer_func(unsigned long data);\n#endif\nstatic void md_cd_traffic_timer_cb')
rep('eccci/hif/ccci_hif_cldma.c','static void cldma_timeout_timer_cb(struct timer_list *t)\n{\n\tstruct md_cd_queue *q = from_timer(q, t, timeout_timer);\n\n\tcldma_timeout_timer_func((unsigned long)q);\n}\n','#ifdef ENABLE_CLDMA_TIMER\nstatic void cldma_timeout_timer_cb(struct timer_list *t)\n{\n\tstruct md_cd_queue *q = from_timer(q, t, timeout_timer);\n\n\tcldma_timeout_timer_func((unsigned long)q);\n}\n#endif\n')
rep('eccci/fsm/ccci_fsm.c','#include "plat_lastbus.h"\n','')
p=R+'eccci/hif/net_speed_monitor.c'
if 'STUB_BR12' not in open(p).read():
    open(p,'w').write('''// SPDX-License-Identifier: GPL-2.0
/* STUB_BR12: net speed monitor (DVFS hint) dimatikan di port 4.19 */
#include <linux/kernel.h>
#include "ccci_hif_internal.h"

static int s_show_speed_inf;

void mtk_ccci_add_dl_pkt_size(int size)
{
}

void mtk_ccci_add_ul_pkt_size(int size)
{
}

int mtk_ccci_toggle_net_speed_log(void)
{
	s_show_speed_inf = !s_show_speed_inf;
	return s_show_speed_inf;
}

int mtk_ccci_speed_monitor_init(void)
{
	return 0;
}
''')
rep('eccci/fsm/ccci_fsm.c','\t\ttimeout_dump();\n','\t\t/* timeout_dump(): lastbus tidak ada di 4.19 */\n')
# header dari ref_oc (4.14 yang jalan)
ROOT=sys.argv[1]
for h in ('include/memory/mediatek/emi.h','include/linux/soc/mediatek/mtk_sip_svc.h'):
    d=ROOT+'/'+h
    if not os.path.exists(d):
        os.makedirs(os.path.dirname(d),exist_ok=True)
        shutil.copy(sys.argv[2]+'/'+h,d)
# ---- link fix: rps, dvfsrc stub, vmap_reserved_mem
p=R+'Makefile'; m=open(p).read()
if 'obj-y += rps/' not in m:
    a='obj-y += devinfo/\n'; assert m.count(a)==1
    open(p,'w').write(m.replace(a,a+'obj-y += rps/\n'))
p=R+'shim/stub.c'; m=open(p).read()
if 'BR12_LINKFIX' not in m:
    open(p,'a').write("""
/* BR12_LINKFIX */
#include <linux/vmalloc.h>
#include <linux/mm.h>
#include <linux/pfn.h>
#include <linux/mmzone.h>
void dvfsrc_mdsrclkena_control(bool on) {}
void *vmap_reserved_mem(phys_addr_t start, phys_addr_t size, pgprot_t prot)
{
	long i;
	long page_count = DIV_ROUND_UP(size, PAGE_SIZE);
	void *vaddr;
	phys_addr_t addr = start;
	struct page **pages = vmalloc(page_count * sizeof(struct page *));

	if (!pages)
		return NULL;
	for (i = 0; i < page_count; i++) {
		pages[i] = pfn_to_page(__phys_to_pfn(addr));
		addr += PAGE_SIZE;
	}
	vaddr = vmap(pages, page_count, VM_MAP, prot);
	vfree(pages);
	return vaddr;
}
EXPORT_SYMBOL(vmap_reserved_mem);
""")
print('fix_br12 OK')
