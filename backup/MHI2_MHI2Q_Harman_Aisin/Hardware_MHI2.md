# Hardware MHI2

## Front cover

 ![MHI2 unit with a SIM card slot (LTE module)](/api/attachments.redirect?id=35e62ca3-6d80-424d-858d-e6b60c2383be)

## RCC (Radio and Car Control) Mainboard / PCB (Printed Circuit Board)

 ![RCC board bottom view. Chips: RCC, NOR, IOC (Renesas V850) ](/api/attachments.redirect?id=faecbda8-44a6-48c9-aeee-2491aea8de38)

\n   ![RCC board top view with MMX board top view on top ](/api/attachments.redirect?id=71c335db-bbf3-40b2-91f8-073ae2cbe10a)       ![RCC board top view with MMX board removed](/api/attachments.redirect?id=8a296985-2a7b-46fd-98ba-b4a6b101ee23)

## MMX (Multi Media eXtension) Mainboard / PCB (Printed Circuit Board)

 ![MMX board top view. Chips: Tegra30, NAND, 4xSDRAM ](/api/attachments.redirect?id=953c3d7c-8f8f-4f3a-82e7-b0d7d14de818)

 ![MMX board bottom view. Chips: NOR ](/api/attachments.redirect?id=fd82e12e-f7c2-469d-996d-9142df7c54bd)

\
 ![MMX board chip details](/api/attachments.redirect?id=0fb20843-25dd-4fee-9bfc-9b5b4e6c0e6c)

## MMX - alternative PCB layouts

Over time different MMX PCB layouts can be found in MHI2 units (see also above) ![](/api/attachments.redirect?id=27c82043-d800-40fe-a198-9e366401bf3d)MMX Tegra30 Peripherals / Pinouts

[Tegra3_publicTRM_DP05644001_v03.pdf 23726005](/api/attachments.redirect?id=6f30c417-2c55-445a-bc10-68b2c120b8b4)

UARTD is exposed as the MMX UART console on the quadlock

NOR is at 0x48000000

USB0 is normal connection, USB3 is also configured in QNX

MMC/SD

* sda: 0x78000000 (SDMMC-1) bs=cd=D3:wp=V2:rs=V6
* sdb: 0x78000400 (SDMMC-3) bs=cd=D4:wp=V3:rs=V7

WLAN

* io-sdiorm-mib2 -p33 -c45000000 -h ioport=0x78000200,irq=47,inpclk=45000000

You can find more addresses in **/net/mmx/mnt/system/etc/boot/startup.sh**


:::info
[MMX board on the MHI2Q](https://mibwiki.one/doc/mhi2q-qualcomm-OjscS91N94) does not have Tegra30, NOR and NAND chips. They are replaced with Qualcomm and eMMC chips.

:::

\
