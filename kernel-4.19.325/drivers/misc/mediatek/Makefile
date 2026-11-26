export MTK_PLATFORM := $(subst ",,$(CONFIG_MTK_PLATFORM))

subdir-ccflags-y += -I$(srctree)/drivers/misc/mediatek/include
subdir-ccflags-y += -I$(srctree)/drivers/misc/mediatek/include/mt-plat/$(MTK_PLATFORM)/include/
subdir-ccflags-y += -I$(srctree)/drivers/misc/mediatek/include/mt-plat/
subdir-ccflags-y += -Wno-error -Wno-strict-prototypes
subdir-ccflags-y += -I$(srctree)/drivers/staging/android/ion/mtk

obj-$(CONFIG_MMPROFILE) += mmp/
obj-$(CONFIG_MTK_SYNC) += sync/
obj-$(CONFIG_MTK_SMI_EXT) += smi/
obj-$(CONFIG_MTK_M4U) += m4u/
obj-$(CONFIG_MTK_CMDQ) += cmdq/
obj-$(CONFIG_MTK_LCM) += lcm/
obj-y += video/
obj-y += ext_disp/
obj-$(CONFIG_MTK_LEDS) += leds/
obj-y += shim/
obj-y += base/
obj-$(CONFIG_MTK_BOOT) += boot/
obj-$(CONFIG_MTK_RTC) += rtc/
obj-y += gpu/
obj-y += aee/
obj-y += cmo/
obj-$(CONFIG_MTK_PMIC_NEW_ARCH) += pmic/
obj-$(CONFIG_MTK_PMIC_WRAP_HAL) += pmic_wrap/
obj-$(CONFIG_MTK_PWM) += pwm/
obj-$(CONFIG_MTK_RAM_CONSOLE) += ram_console/
obj-y += atf/

obj-$(CONFIG_MTK_AUXADC) += auxadc/
obj-y += devinfo/
