# -*- coding: utf-8 -*-
"""
Backdropper - Backup to Dropbox.
"""
import os
import dropbox
import argparse
from dropbox.files import WriteMode
from zipfile import ZipFile, ZIP_BZIP2

ACCESS_TOKEN_FILENAME: str = ".token"


class Backdropper:

	def __init__(self, token: str):
		self.token: str = token
		self.dbx: dropbox.Dropbox = dropbox.Dropbox(self.token)
		self.path: str = ''
		self.overwrite: bool = False
		self.success: bool = False

	def _upload_file(self, content: bytes):
		mode = WriteMode("overwrite" if self.overwrite else "add")
		path = self.path if self.path.startswith("/") else f"/{self.path}"
		self.dbx.files_upload(content, path, mode=mode)
		self.success = True

	def _upload_dir_as_zipfile(self, target_dir: str):
		self.path = zipname = f"{self.path}{'' if self.path.endswith('.zip') else '.zip'}"
		zipname = zipname.replace("/", "-")
		with ZipFile(zipname, mode="w", compression=ZIP_BZIP2, compresslevel=9) as z:
			for root, _, files in os.walk(target_dir):
				for f in files:
					z.write(os.path.join(root, f))
		try:
			with open(zipname, "rb") as f:
				zip_content = f.read()
			self._upload_file(zip_content)
		finally:
			os.remove(zipname)

	def upload(self, target, path, overwrite=False):
		"""
		:param str target: Filename or directory name to upload. A directory will be zipped before being uploaded.
		:param str path: The path/filename to save the target under.
		:param bool overwrite: (optional) Overwrite existing file or add under a modified name.
		"""
		self.overwrite = overwrite
		self.path = path
		if os.path.isfile(target):
			with open(target, "rb") as f:
				content = f.read()
			self._upload_file(content)
		elif os.path.isdir(target):
			self._upload_dir_as_zipfile(target)
		else:
			print("Invalid input")


def get_access_token(token_filename: str) -> str:
	with open(token_filename) as f:
		at: str = f.read()
	return at


def create_parser() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("target", action="store", help="The file or directory to upload")
	parser.add_argument("-n", "--name", action="store", help="Alternative path/name to save the target under")
	parser.add_argument("--do-not-overwrite", action="store_false", help="Do not overwrite name if this flag is set")
	parser.add_argument("-t", "--token-file", action="store", default=ACCESS_TOKEN_FILENAME, nargs=1,
	                    help=f"Read token from file. By default look for {ACCESS_TOKEN_FILENAME} in current directory")
	return parser.parse_args()


if __name__ == "__main__":
	args = create_parser()
	bd = Backdropper(get_access_token(args.token_file))
	save_name = args.name or args.target
	bd.upload(args.target, save_name, args.do_not_overwrite)
	print(f"Saving {args.target} to {save_name} {'completed successfully' if bd.success else 'failed'}")
