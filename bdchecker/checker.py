import csv
import hashlib
import logging
import os
import shutil

from bdchecker.utils.log_handle import LogHandle


class Checker:
    """
    backup data checker
    """

    def __init__(self, verbose=0, hash_algo="sha256"):
        """
        init checker
        """
        self._hash_fn = hashlib.sha256
        self._hash_algo = ""
        self._meta_dirname = ".bdchecker.meta"

        if verbose == 0:
            LogHandle.init_log("", logging.INFO, -1)
        elif verbose == 1:
            LogHandle.init_log("", logging.DEBUG, -1)
        else:
            LogHandle.init_log("", logging.DEBUG, -1)

        self._hash_algo = hash_algo
        if hash_algo == "sha256":
            self._hash_fn = hashlib.sha256
        elif hash_algo == "sha512":
            self._hash_fn = hashlib.sha512
        elif hash_algo == "md5":
            self._hash_fn = hashlib.md5
        else:
            self._hash_algo = "sha256"
            self._hash_fn = hashlib.sha256

    def gen(self, dst_dir):
        """
        generate meta infos
        :param dst_dir: target directory
        """
        if not os.path.exists(dst_dir):
            raise Exception("target directory not exists: {}".format(dst_dir))

        # load meta info that already exists
        meta_dir = os.path.join(dst_dir, self._meta_dirname)
        if os.path.exists(meta_dir):
            if not os.path.isdir(meta_dir):
                raise Exception(
                    "{} already exists and not a directory".format(meta_dir))
        else:
            os.makedirs(meta_dir, exist_ok=True)

        # load old meta infos
        meta_filepath = os.path.join(meta_dir, "{}.csv".format(self._hash_algo))

        if os.path.exists(meta_filepath):
            old_meta_dict = self._load_meta(meta_filepath)
        else:
            old_meta_dict = {}

        # scan files and generate new meta info
        meta_dict = self._scan(dst_dir=dst_dir)

        for k, v in old_meta_dict.items():
            if k not in meta_dict:
                logging.warning("missing file: {}".format(k))
            meta_dict[k] = v

        n_new = 0
        for k in meta_dict.keys():
            if k not in old_meta_dict:
                filepath = os.path.join(dst_dir, k)
                hash_val_hex = self._gen_hash(filepath)
                logging.debug("new file: {}, hash value: {}".format(
                    k, hash_val_hex))
                meta_dict[k] = hash_val_hex
                n_new += 1

        # write into file
        if n_new > 0:
            self._dump_meta(meta_filepath, meta_dict)
        else:
            logging.info("there are no new file in {}".format(dst_dir))

    def clean(self, dst_dir):
        """
        clean
        """
        if not os.path.exists(dst_dir):
            raise Exception("target directory not exists: {}".format(dst_dir))

        # load meta info that already exists
        meta_dir = os.path.join(dst_dir, self._meta_dirname)
        if os.path.exists(meta_dir):
            if not os.path.isdir(meta_dir):
                raise Exception(
                    "{} already exists and not a directory".format(meta_dir))
        else:
            os.makedirs(meta_dir, exist_ok=True)

        # load old meta infos
        meta_filepath = os.path.join(meta_dir, "{}.csv".format(self._hash_algo))

        if os.path.exists(meta_filepath):
            old_meta_dict = self._load_meta(meta_filepath)
        else:
            old_meta_dict = {}

        # scan files and remove meta info of missing file
        meta_dict = self._scan(dst_dir=dst_dir)

        missing_files = []
        for k in old_meta_dict.keys():
            if k not in meta_dict:
                logging.info("clean missing file's meta info: {}".format(k))
                missing_files.append(k)

        for filepath in missing_files:
            del old_meta_dict[filepath]

        if len(missing_files) > 0:
            self._dump_meta(meta_filepath, old_meta_dict)
        else:
            logging.info("there are no missing file in {}".format(dst_dir))

    def check(self, dst_dir):
        """
        check meta infos
        :param dst_dir: target directory
        """
        if not os.path.exists(dst_dir):
            raise Exception("target directory not exists: {}".format(dst_dir))

        # load meta info that already exists
        meta_dir = os.path.join(dst_dir, self._meta_dirname)
        if os.path.exists(meta_dir):
            if not os.path.isdir(meta_dir):
                raise Exception(
                    "{} already exists and not a directory".format(meta_dir))
        else:
            os.makedirs(meta_dir, exist_ok=True)

        # load old meta infos
        meta_filepath = os.path.join(meta_dir, "{}.csv".format(self._hash_algo))

        if not os.path.exists(meta_filepath):
            logging.error("can't check cause meta file not found: {}".format(
                meta_filepath))
        old_meta_dict = self._load_meta(meta_filepath)

        # scan files and generate new meta info
        meta_dict = self._scan(dst_dir=dst_dir)
        for k, v in meta_dict.items():
            filepath = os.path.join(dst_dir, k)
            hash_val_hex = self._gen_hash(filepath)
            meta_dict[k] = hash_val_hex
            logging.debug(
                "calculate hash value: {}, {}".format(k, hash_val_hex))

        for k, v in old_meta_dict.items():
            if k not in meta_dict:
                logging.warning("missing file: {}".format(k))

        for k, v in meta_dict.items():
            if k not in old_meta_dict:
                logging.warning("new file: {}".format(k))

            old_v = old_meta_dict[k]
            if v != old_v:
                logging.error(
                    "check failed: {}, old hash: {}, cur hash: {}".format(
                        k, old_v, v))

    def _dump_meta(self, meta_filepath, meta_dict):
        """
        dump meta infos
        """
        backup_filepath = "{}.backup".format(meta_filepath)
        tmp_meta_filepath = "{}.tmp".format(meta_filepath)

        # backup
        if os.path.exists(meta_filepath):
            shutil.copyfile(meta_filepath, backup_filepath)

        # dump
        logging.info("dump meta info to {}".format(meta_filepath))
        sorted_dict = dict(sorted(meta_dict.items()))
        with open(tmp_meta_filepath, "w") as f:
            writer = csv.writer(f, delimiter=",")
            writer.writerow(["k", "v"])
            for k, v in sorted_dict.items():
                writer.writerow([k, v])
        shutil.move(tmp_meta_filepath, meta_filepath)

        # remove backup file
        if os.path.exists(backup_filepath):
            os.remove(backup_filepath)

    def _scan(self, dst_dir):
        """
        scan dst dir and get file dict with empty hash value
        :param dst_dir: target directory
        """
        logging.info("start scan: {}".format(dst_dir))
        meta_dict = {}
        for root, _, files in os.walk(dst_dir):
            for filename in files:
                sub_dirname = os.path.basename(os.path.normpath(root))
                if sub_dirname == self._meta_dirname:
                    continue
                dir_relpath = os.path.relpath(root, dst_dir)
                rel_filepath = os.path.join(dir_relpath, filename)
                rel_filepath = os.path.normpath(rel_filepath)
                rel_filepath = rel_filepath.replace("\\", "/")
                meta_dict[rel_filepath] = ""
        return meta_dict

    def _gen_hash(self, filepath):
        """
        generate hash value
        :param filepath:
        """
        block_size = 1024 * 32
        hash_val = self._hash_fn()
        with open(filepath, "rb") as f:
            while True:
                block = f.read(block_size)
                if not block:
                    break
                hash_val.update(block)
        return hash_val.hexdigest().upper()

    def _load_meta(self, filepath):
        """
        load meta info
        :param filepath: meta filepath
        """
        logging.info("start load meta file: {}".format(filepath))
        meta_dict = {}
        with open(filepath, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                meta_dict[row["k"]] = row["v"]
                logging.debug("{}: {}".format(row["k"], row["v"]))
        return meta_dict
