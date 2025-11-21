# Manual IOC Update via telnet or TTL cable


> [!WARNING]
> Proceed only if you clearly understand what you’re doing
> 
> It is assumed you know how to connect to RCC or MMX via [telnet or serial port](https://mibwiki.one/doc/shell-access-via-telnet-and-uart-6ojvSNAqui)
> 
> You must have reliable FAT32 formatted SD card ready
> [!INFO]
> V850app controls EEPROM access. V850bolo powers on the unit. Damaged bolo leads to non working buttons/touch screen
First of all clarify, which variant does your unit have (for example FM2-P-TNL-JP-AU-MLE). 

You can find out in m.i.b. installation log or just login to RCC/MMX and check with:

```none
cat /net/rcc/mnt/efs-persist/SWDL/CachedTrain.txt
```

# MHIG and MHI2_XX_AUG22


1. Take a look into firmware installation SD in metainfo2.txt and find references of your variant to files in **\\IOC\\Main\\40\\default** 
2. Copy V850app and V850bolo corresponding to your variant **to the root of SD card** formatted in FAT32 and rename:

   ```none
   V850app_MLBEVO.bin > ioc_appl_bin_todo
   V850bolo_MLBEVO.bin > ioc_bolo_bin_todo
   ```
3. Safely eject the SD and insert into SD1 slot of MIB
4. Reboot the unit and IOC update will start automatically


> [!INFO]
> If you want to see what happens, connect with TTL adapter to RCC on the quadlock, log in to [Emergency IFS](https://mibwiki.one/doc/how-to-stop-ipl-enter-cli-boot-ifs-emergencyifs-and-restore-ifsroot-stage2-jnQb14ZDOs) and run:
```none
on -f rcc /net/rcc/sbin/mib_ioc_update -h
```

\
# MHI2


1. Take a look into firmware installation SD in metainfo2.txt and find references of your variant to files in **\\IOC\\Main\\21\\default** 

   
> [!INFO]
>    e.g. Audi A6 has FM2-H-\*\*\****-*\*\***-AU-MLB
> 
>    :::
> 2. Create IOC folder on SD card
> 3. Take a look into metainfo2.txt and copy V850app and V850bolo corresponding to your variant **to the IOC folder of SD card** formatted in FAT32 
> 
>     ![](assets/6fe9ce58-8537-4da3-bb79-04401dc6d956.redirect_id_6fe9ce58-8537-4da3-bb79-04401dc6d956)
> 
>    In our case V850appMLB.bin and V850boloMLB.bin
> 4. Rename the files you copied to IOC folder:
> 
>    ```none
>    V850app_MLB.bin > ioc_appl_bin
>    V850bolo_MLB.bin > ioc_bolo_bin
>    ```
> 5. Safely eject the SD and insert into SD1 of MIB
> 
> 
> :::warning
> ALWAYS flash APP before BOLO.
> 
> If you do it the other way around you will loose connection to EEPROM, key input on screen and SWDL will stop working.
## Reboot unit in update mode to update IOC App

`on -f rcc /usr/apps/mib2_ioc_flash updateApp`

Unit will restart automatically and you will see update reboot screen on MMI

 ![](assets/7f97681e-acda-4fa5-9bf4-8d16c336b0e5.redirect_id_7f97681e-acda-4fa5-9bf4-8d16c336b0e5)

## Update IOC App

`on -f rcc /usr/apps/mib2_ioc_flash updateAppNow`

 ![](assets/96a330be-3aba-4696-a81a-d2dd45836d14.redirect_id_96a330be-3aba-4696-a81a-d2dd45836d14)

## Restart unit (if no automatic reboot was triggered)

`on -f rcc /usr/apps/mib2_ioc_flash reboot`

## Run unit in update mode to update IOC Bolo

`on -f rcc /usr/apps/mib2_ioc_flash updateBolo`

Automatic restart will be triggered again and unit goes into boot mode

\
## Update IOC Bolo

`on -f rcc /usr/apps/mib2_ioc_flash updateBoloNow`

 ![](assets/4508a0ef-d4e0-45d8-983d-bc8f5765df7d.redirect_id_4508a0ef-d4e0-45d8-983d-bc8f5765df7d)

\
# Known issues

If you updated Bolo before App, RCC and MMX will loose EEPROM access and Train version and MU software will look like:

 ![EEPROM can not be acessed](assets/fd8d399b-d6fa-4e1c-a535-df701070bf60.redirect_id_fd8d399b-d6fa-4e1c-a535-df701070bf60)

To fix this, repeat the steps starting from updateApp

# Reference

[IOC Update.pdf](assets/0404838e-efa5-4a42-b945-b18f036170d6.redirect_id_0404838e-efa5-4a42-b945-b18f036170d6)

\
