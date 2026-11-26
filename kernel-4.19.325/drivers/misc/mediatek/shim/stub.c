#include <linux/device.h>
#include <linux/init.h>
#include <linux/err.h>
#include <linux/export.h>


/* class "sec" dibuat oleh drivers/samsung/sec_class.c */


/* stub link-only (A02 4.19 bootstrap) */
int vcorefs_request_dvfs_opp(int kicker, int opp) { return 0; }
void spm_sodi_mempll_pwr_mode(bool m) {}
void spm_enable_sodi(bool en) {}
void spm_enable_sodi3(bool en) {}
void spm_sodi_set_vdo_mode(bool m) {}
void tracing_mark_write(const char *fmt, ...) {}
int mt_spower_get_leakage(int dev, unsigned int vol, int deg) { return 0; }
int mt_spower_init(void) { return 0; }
void dvfsrc_mdsrclkena_control_nolock(bool on) {}
void __inner_flush_dcache_L1(void) {}
void __inner_flush_dcache_L2(void) {}
void __inner_flush_dcache_all(void) {}
void __disable_dcache(void) {}
void register_low_battery_notify(void (*cb)(int), int prio) {}
void register_battery_percent_notify(void (*cb)(int), int prio) {}
void register_battery_oc_notify(void (*cb)(int), int prio) {}
void mtk_gpufreq_register(void *freqs, int num) {}
int mt_dfs_general_pll(unsigned int pll, unsigned int dds) { return 0; }
void mmdvfs_set_max_camera_hrt_bw(u32 bw) {}
int mmdvfs_qos_get_freq_steps(u32 cls, u64 *steps, u32 *num) { return 0; }
int mdp_limit_late_init(void) { return 0; }
int mdp_limit_dev_create(void *dev) { return 0; }
void mdp_limit_dev_destroy(void) {}
int mdp_ioctl_async_exec(void) { return -EINVAL; }
int mdp_ioctl_async_exec_sz(void) { return -EINVAL; }
int mdp_ioctl_async_wait(void) { return -EINVAL; }
int mdp_ioctl_alloc_readback_slots(void) { return -EINVAL; }
int mdp_ioctl_free_readback_slots(void) { return -EINVAL; }
int mdp_ioctl_read_readback_slots(void) { return -EINVAL; }
void mdp_ioctl_free_job_by_node(void) {}

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
