#!/usr/local/env python3
"""
Backdropper - Backup to Dropbox.
"""
import os
import json
import dropbox
import argparse
from dropbox.files import WriteMode
from zipfile import ZipFile, ZIP_BZIP2

SECRETS_FILENAME = ".secrets.json"


class Backdropper:

	def __init__(self, secrets_filename=SECRETS_FILENAME):
		self.secrets_filename = secrets_filename
		self.secrets: dict = {}
		self.dbx: dropbox.Dropbox | None = None
		self.path: str = ""
		self.overwrite: bool = False
		self.success: bool = False
		self._get_secrets()
		self._authorize()

	def _get_secrets(self):
		with open(self.secrets_filename) as f:
			self.secrets: dict = json.loads(f.read())

	def _save_secrets(self):
		with open(self.secrets_filename, "w", encoding="utf-8") as f:
			f.write(json.dumps(self.secrets, indent=2))

	def _authorize(self):
		if self.secrets.get("refresh_token"):
			self.dbx = dropbox.Dropbox(app_key=self.secrets["app_key"], app_secret=self.secrets["app_secret"],
									   oauth2_refresh_token=self.secrets["refresh_token"])
		else:
			oauth_flow = dropbox.oauth.DropboxOAuth2FlowNoRedirect(
				self.secrets["app_key"], self.secrets["app_secret"], token_access_type="offline")
			authorize_url = oauth_flow.start()
			print(f"1. Go to {authorize_url}")
			print("2. Click 'Allow (you might have to log in first).")
			print("3. Copy the authorization code.")
			auth_code = input("Enter the authorization code here: ")
			oauth_result = oauth_flow.finish(auth_code)
			access_token = oauth_result.access_token
			self.dbx = dropbox.Dropbox(access_token)
			self.secrets["refresh_token"] = oauth_result.refresh_token
			self._save_secrets()

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

	def upload(self, target: str, path: str, overwrite: bool = False):
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


def create_parser() -> argparse.Namespace:
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument("target", action="store", help="The file or directory to upload")
	parser.add_argument("-n", "--name", action="store", help="Alternative path/name to save the target under")
	parser.add_argument("--do-not-overwrite", action="store_false", help="Do not overwrite name if this flag is set")
	parser.add_argument("-s", "--secrets-filename", action="store", default=SECRETS_FILENAME,
						help=f"Read secrets from file. By default look for {SECRETS_FILENAME} in current directory")
	return parser.parse_args()


if __name__ == "__main__":
	args = create_parser()
	bd = Backdropper(args.secrets_filename)
	save_name = args.name or args.target
	bd.upload(args.target, save_name, args.do_not_overwrite)
	print(f"Saving {args.target} to {save_name} {'completed successfully' if bd.success else 'failed'}")
