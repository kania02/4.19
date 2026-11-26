// SPDX-License-Identifier: GPL-2.0
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
