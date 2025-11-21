# ----------------------------------------------------------
# --- Update the hashes in the repo
#
# File:        update-hashes.py
# Author:      andrewleech
# Revision:    1
# Purpose:     Update all sha1 hashes and hash files
# Comments:    Usage: python update-hashes.py
# ----------------------------------------------------------

import re
import sys
import time
import logging
import difflib
import hashlib
import binascii
import argparse
import datetime
from pathlib import Path
from __version__ import version
try:
    from typing import *
except ImportError:
    pass

from configobj import ConfigObj


repo = None


donor_header = b"""\
[common]
vendor = "ESO"
variant = "FMU-H-*-*-*"
variant2 = "FM2-*-*-*-*"
variant3 = "QC2-*-*-*-*"
variant4 = "FMQ-*-*-*-*"
region = "RoW"
MetafileChecksum = "37259e4758d7c843f316aaaa306cced5211049cf"

[common_Release_1]
variant = "FMU-H-*-*-*"
region = "RoW"
name = "MIB1 navigation database"
path = "./Mib1"

[common_Release_2]
variant = "FM2-*-*-*-*"
variant2 = "QC2-*-*-*-*"
variant3 = "FMQ-*-*-*-*"
region = "RoW"
name = "MIB2 navigation database"
path = "./Mib2"

[Signature]
signature1 = "11583e2be1780d5ee04eb62c71e0d2f1"
signature2 = "dab4162103aaf3a6497f8fd30e97c290"
signature3 = "ee7d5c8d35bf53c29a8bbc2474c42175"
signature4 = "ba89fea84694df7b8c3da7de41b82da6"
signature5 = "cb39043600b6de3fe728adcba7148652"
signature6 = "b6b7989079d3f2f44bcec54ef59212a2"
signature7 = "133f9224b6bcc4492e6818b1475a7d83"
signature8 = "0dde6b0489314cf4924be9e2e91db990"

"""

# track changes
__changed__ = []


def backup(f: Path):
    timestr = time.strftime("%Y%m%d-%H%M%S")
    newname = f.with_name(f"._{f.name}_{timestr}")
    __changed__.append((f, newname))
    f.rename(newname)


def file_hash(path, checksumsize=524288, current=None):
    with open(path, 'rb') as f:
        if checksumsize != 0:
            length = 0
            digests = []
            first = True
            while True:
                hasher = hashlib.sha1()
                buf = f.read(checksumsize)
                hasher.update(buf)
                if len(buf) == 0:
                    break
                length += len(buf)
                fhash = hasher.hexdigest()
                if current and first and fhash == current.strip('"'):
                    raise StopIteration
                first = False
                digests.append(f'"{fhash}"')
            return length, digests
        else:
            hasher = hashlib.sha1()
            buf = f.read()
            hasher.update(buf)
            fhash = hasher.hexdigest()
            if current and fhash == current:
                raise StopIteration
            return len(buf), [f'"{fhash}"']


class HashFileDef:
    def __init__(self, FileName, FileSize, shas, CheckSumSize, idx=0):
        self.FileName = FileName
        self.FileSize = int(FileSize)
        self.shas = shas
        self.CheckSum = self.shas[0]
        self.CheckSumSize = CheckSumSize
        self.idx = idx

    @classmethod
    def parse(self, chunk, idx):
        FileName = re.findall(r'FileName = "*(.+?)"*\s', chunk)[0]
        FileSize = int(re.findall(r'FileSize = "*(.+?)"*\s', chunk)[0])
        shas = re.findall(r'CheckSum\d* = "*(.+?)"*\s', chunk)
        CheckSumSize = int([*re.findall(r'CheckSumSize = "*(.+?)"*\s', chunk), 0][0])
        return HashFileDef(FileName, FileSize, shas, CheckSumSize, idx)

    def __eq__(self, other):
        if isinstance(other, HashFileDef):
            return self.FileName == other.FileName and self.CheckSum == other.CheckSum
        else:
            return self.FileName == other

    def __str__(self):
        chunk = f'FileName = "{self.FileName}"'
        chunk += f'\nFileSize = "{self.FileSize}"'
        if self.CheckSumSize:
            chunk += f'\nCheckSumSize = "{self.CheckSumSize}"'
        for n, sha in enumerate(self.shas):
            n = '' if n == 0 else str(n)
            sha = sha.strip('"')
            chunk += f'\nCheckSum{n} = "{sha}"'
        return chunk + '\n'

    def __repr__(self):
        return self.__str__()


def generate_hashes(path, checksumsize=524288):
    finalhash = path / 'hashes.txt'

    # Generate hashes.txt
    final_dir_size = 0
    hashes_text = ''
    hashes_text_orig = finalhash.read_bytes() if finalhash.exists() else b''
    header_split = re.search(b'^FileName =', hashes_text_orig, re.MULTILINE)
    if header_split:
        hashes_text_header = hashes_text_orig[0:header_split.start()]
        hashes_text_content = hashes_text_orig[header_split.start():]
    else:
        hashes_text_header = b''
        hashes_text_content = hashes_text_orig
    endings = b'\r\n' if b'\r\n' in hashes_text_content else b'\n'
    hashes_text_content = hashes_text_content.replace(b'\r\n', b'\n').decode()
    trailing_newlines = len(hashes_text_content) - len(hashes_text_content.rstrip('\n'))

    hashes_text = []

    hashes_chunks = re.split("(^FileName )", hashes_text_content, flags=re.MULTILINE)
    hashes_chunks = [f'FileName {c}' for c in hashes_chunks[1:] if c != 'FileName ']

    n = len(hashes_chunks)
    hashes_chunks = [HashFileDef.parse(chunk, n - i) for i, chunk in enumerate(hashes_chunks)]  # type: List[HashFileDef]

    def hash_dir(p, stem=''):
        nonlocal hashes_chunks, hashes_text, final_dir_size, checksumsize
        for f in p.iterdir():
            if f == finalhash:
                continue
            elif f.name.startswith("."):
                # ignore "hidden" files
                continue
            elif f.is_dir():
                hash_dir(f, stem=f'{stem}{f.name}/')
            else:
                filename = stem + f.name
                idx = 0
                current = existing = existing_css = None
                if filename in hashes_chunks:
                    index = hashes_chunks.index(filename)
                    existing = hashes_chunks[index]
                    current = existing.CheckSum
                    existing_css = existing.CheckSumSize
                    idx = existing.idx
                else:
                    logging.warning(f"** New file being added to hashes: {f}")

                try:
                    size, shas = file_hash(f, existing_css or checksumsize, current=current)
                    css = existing_css
                    if not size:
                        continue
                    if len(shas) > 1:
                        css = checksumsize
                    if not shas:
                        print(f"FAIL: {shas} {f}")
                    chunk = HashFileDef(FileName=filename, FileSize=size, shas=shas, idx=idx, CheckSumSize=css)
                    hashes_text.append(chunk)

                except StopIteration:
                    hashes_text.append(existing)
                    size = existing.FileSize

                final_dir_size += size

    hash_dir(path)
    # Preserve original file order
    hashes_text.sort(key=lambda chunk: chunk.idx, reverse=True)

    new_text = '\n'.join([str(c) for c in hashes_text])

    footer_len = len(new_text) - len(new_text.rstrip('\n'))
    if trailing_newlines > footer_len:
        new_text += '\n' * (trailing_newlines - footer_len)

    new_text = new_text.encode().replace(b'\n', endings)  # ensure line endings match original
    new_text = hashes_text_header + new_text
    if new_text != hashes_text_orig:
        backup(finalhash)
        finalhash.write_bytes(new_text)
        logging.info(f"hashes.txt: Updated details in {finalhash}")
    final_dir_size += len(new_text)
    return finalhash, final_dir_size


def handle_common_final(config):
    changed = False
    finalscript = repo / config['common']['FinalScript'].strip('"')
    common_dir_block = str(Path(config['common']['FinalScript'].strip('"')).parent / "dir").lower().replace('/', '\\')
    if common_dir_block.startswith('.\\'):
        common_dir_block = common_dir_block[2:]
    for s in config.sections:
        if s.lower() == common_dir_block.lower():
            common_dir_block = s
            break

    finalhash, final_dir_size = generate_hashes(finalscript.parent)

    _, finalscript_hash = file_hash(finalscript)
    current = config['common']['FinalScriptChecksum']
    if finalscript_hash[0] != current:
        logging.info("\nmetainfo2.txt: Updated FinalScriptChecksum")
    changed |= config_set_key(config, 'common', 'FinalScriptChecksum', finalscript_hash[0])

    _, curr_finalhash_hash = file_hash(finalhash)
    if common_dir_block not in config:
        logging.info("\nMissing block:", common_dir_block)
        # config.add_section(common_dir_block)
    current = config[common_dir_block].get('CheckSum')
    if current.lower() != curr_finalhash_hash[0].lower():
        logging.info("\nmetainfo2.txt: Updated FinalScript block details")
    changed |= config_set_key(config, common_dir_block, 'CheckSum', curr_finalhash_hash[0].upper())
    changed |= config_set_key(config, common_dir_block, 'FileSize', '"%i"' % final_dir_size)

    return common_dir_block, changed


def config_remove_key(config, section, key):
    try:
        config[section][key]
    except KeyError:
        return False
    del config[section][key]
    return True


def config_set_key(config, section, key, value):
    changed = False
    try:
        current = config[section][key]
    except KeyError:
        current = ''
        changed = True
    if current.upper() != value.upper():
        changed = True
    if changed:
        config[section][key] = value
    return changed


def update_muconsistency(muconsistency_file):
    try:
        muc_details = muconsistency_file.read_bytes()
        pattern = b'(\[CRC\]\r?\n)\S\S\S\S\S\S\S\S'
        crc = binascii.crc32(re.sub(pattern, b'[CRC]', muc_details, flags=re.MULTILINE))
        hexcrc = f'{crc:08x}'
        new_muc_details = re.sub(pattern, b'\g<1>%s' % hexcrc.encode(), muc_details, flags=re.MULTILINE)
        if muc_details.lower() != new_muc_details.lower():
            logging.info("Updating muconsistency CRC")
            backup(muconsistency_file)
            muconsistency_file.write_bytes(new_muc_details)
    except IndexError:
        logging.error('Error in muconsistency parsing; could not find files')


def update_checksums(check_all, config, section, source, checksumsize, changed):
    try:
        if check_all:
            # Don't compare to existing checksum
            current = None
        else:
            # If first block of checksum matches, skip reading the rest of the file (faster)
            current = config[section][f'CheckSum']
        filesize, shas = file_hash(source, checksumsize, current=current)
        changed |= config_set_key(config, section, 'FileSize', '"%i"' % filesize)
        for n, sha in enumerate(shas):
            strn = '' if n == 0 else str(n)
            changed |= config_set_key(config, section, f'CheckSum{strn}', sha.upper())
        while config_remove_key(config, section, f'CheckSum{n + 1}'):
            n += 1
    except StopIteration:
        pass
    return changed


def main():
    parser = argparse.ArgumentParser(prog='update_hashes', description=f"MIB2 metinfo2.txt hash updater version {version}")
    parser.add_argument("target", nargs="?", default='.', help="target file/folder")
    parser.add_argument("-v", "--version", action="store_true", help="report version number")
    parser.add_argument("-c", "--checksums", action="store_true", help="Thoroughly re-check checksums, default is to only check first block")

    args = parser.parse_args()
    if args.version:
        print(version)
        return

    global repo
    taget = Path(args.target)
    if taget.is_dir():
        repo = taget
        metainfo = repo / 'metainfo2.txt'

    else:
        metainfo = taget
        repo = metainfo.parent

    if not metainfo.exists():
        raise SystemExit(f"Cannot find metainfo2.txt at: {metainfo.resolve(strict=False)}")

    logging.basicConfig(filename=repo / 'update-hashes.log', level=logging.DEBUG)
    logging.getLogger().addHandler(logging.StreamHandler())

    logging.info('==========================================================================================')
    logging.info(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    logging.info(f"Parsing: {metainfo.resolve()}")
    logging.info('==========================================================================================')

    metainfo_contents = metainfo.read_bytes()
    windows_line_ending = b'\r\n' in metainfo_contents
    metainfo_contents = metainfo_contents.replace(b'\r\n', b'\n')  # Ensure LF line endings while building

    # split metainfo into original and new parts
    metainfo_splits = re.findall(b'^signature\d* = "\S+"\n?', metainfo_contents, flags=re.MULTILINE)
    divide = metainfo_contents.index(metainfo_splits[-1])
    divide += len(metainfo_splits[-1])
    metainfo_orig = metainfo_contents[0:divide]
    metainfo_new = metainfo_contents[divide + 1:]

    added_donor = False

    if not metainfo_new.strip():
        logging.warning("metainfo2.txt: No donor header, adding now...")
        metainfo_new = re.split(b'^\[Signature\]', metainfo_orig, flags=(re.IGNORECASE | re.MULTILINE))[0]
        metainfo_orig = donor_header
        added_donor = True

    lines = metainfo_new.split(b'\n')

    config = ConfigObj(lines, list_values=False)

    common_dir = None

    # Need to update ImageLayout2 sections last after the sections they reference have been handled
    all_sections = [s for s in config.sections if 'ImageLayout2' not in s]
    imagelayout2_sections = [s for s in config.sections if 'ImageLayout2' in s]

    all_sections.extend(imagelayout2_sections)

    # Calculate hashes and updates for each section
    for section in all_sections:
        log = []
        changed = False
        title = f"metainfo2.txt: {section}"
        log.append(title + (" " * (max(0, 80 - len(title)))))
        try:
            if section == "common":
                if 'MetafileChecksum' in config[section]:
                    del config[section]['MetafileChecksum']
                    changed = True
                if 'FinalScript' in config[section]:
                    try:
                        common_dir_block, changed = handle_common_final(config)
                    except KeyError:
                        pass
                if added_donor:
                    dev_flags = ('checkIfNotEqual', 'skipCheckRegion', 'checkAllUpdates', 'skipCheckSignatureAndVariant', 'delMmeBackup')
                    for flag in dev_flags:
                        if flag not in config[section] and ('#'+flag) not in config[section]:
                            config[section]['#'+flag] = True

            elif common_dir and section.lower() == common_dir:
                # already handled above
                pass

            else:
                if 'scriptPreCheckSum' in config[section]:
                    filename = repo / config[section]['scriptPre'].strip('"')
                    checksumsize = int(config[section].get('CheckSumSize', '524288').strip('"'))
                    _, shas = file_hash(filename, checksumsize)
                    changed |= config_set_key(config, section, 'scriptPreCheckSum', shas[0].upper())

                if 'scriptPostCheckSum' in config[section]:
                    filename = repo / config[section]['scriptPost'].strip('"')
                    checksumsize = int(config[section].get('CheckSumSize', '524288').strip('"'))
                    _, shas = file_hash(filename, checksumsize)
                    changed |= config_set_key(config, section, 'scriptPostCheckSum', shas[0].upper())

                if 'ImageLayout2' in section:
                    ref_stub = 'RCC' + section.split('ImageLayout2')[1]
                    try:
                        ref_section = [s for s in config.sections if s.startswith(ref_stub)][0]
                    except IndexError:
                        log.append(f"Warn: Could not for reference for {section}")
                        continue

                if 'CheckSum' in config[section]:
                    section_path = repo / section.strip('"')
                    source = section_path.parent
                    stype = section_path.name.lower()
                    checksumsize = int(config[section].get('CheckSumSize', '524288').strip('"'))
                    if stype.startswith("filter:"):
                        section_path = section_path.parent
                        source = section_path.parent
                        stype = section_path.name.lower()
                    if stype == 'dir':
                        if 'Source' in config[section]:
                            source = source / config[section]['Source'].strip('"')
                        if not source.is_dir():
                            log.append(f"Inconsistent dir/file for {source}")
                            continue
                        hashfile, hashfile_dir_size = generate_hashes(source)
                        changed |= config_set_key(config, section, 'FileSize', '"%i"' % hashfile_dir_size)
                        _, shas = file_hash(hashfile, checksumsize)
                        changed |= config_set_key(config, section, 'CheckSum', shas[0].upper())
                    elif stype == 'file':
                        if 'Source' not in config[section]:
                            log.append(f'Source missing from {section}')
                            continue
                        source = source / config[section]['Source'].strip('"')
                        if not source.exists():
                            log.append('File missing: {source}')
                            continue
                        if 'muconsistency' in section.lower():
                            update_muconsistency(source)

                        changed = update_checksums(check_all=args.checksums, config=config, section=section,
                                                   source=source, checksumsize=checksumsize, changed=changed)
                        
                    elif stype == 'application' or stype == 'bootloader':
                        if 'FileName' not in config[section]:
                            log.append(f'FileName missing from {section}')
                            continue
                        source = source / config[section]['FileName'].strip('"')
                        if not source.exists():
                            log.append('File missing: {source}')
                            continue
                        changed = update_checksums(check_all=args.checksums, config=config, section=section,
                                                   source=source, checksumsize=checksumsize, changed=changed)
                    else:
                        log.append(f"Don't know how to process: {section_path}")
        except:
            logging.exception(f"Error parsing section: {section}")
        finally:
            if changed:
                log.append("UPDATED")
            elif len(log) == 1:
                log.append("-------")

            logging.info(" | ".join(log))

    lines = config.write()

    metainfo_contents = '\n'.join([metainfo_orig.decode(), *lines])

    if windows_line_ending:
        # metainfo needs to be CRLF to maintain original crc's
        metainfo_contents = metainfo_contents.replace('\n', '\r\n')

    backup(metainfo)
    metainfo.write_bytes(metainfo_contents.encode())

    # write diff file
    timestr = time.strftime("%Y%m%d-%H%M%S")
    difflog_path = repo / f"update-hashes_{timestr}.diff"
    logging.info(f"Writing diff to: {difflog_path}")
    with Path(difflog_path).open('w') as difflog:
        for updated, orig in __changed__:
            with open(orig) as f:
                olines = f.readlines()
            with open(updated) as f:
                ulines = f.readlines()

            diff = difflib.unified_diff(
                olines,
                ulines,
                fromfile=f"{updated} (original)",
                tofile=str(updated),
                n=5
            )
            difflog.writelines(diff)

    logging.info("Finished")


if __name__ == '__main__':
    try:
        main()
    except:
        logging.exception("Unexpected Failure")
    finally:
        time.sleep(2)
