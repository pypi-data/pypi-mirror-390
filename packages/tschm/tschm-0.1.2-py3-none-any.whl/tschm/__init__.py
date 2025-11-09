

import fire
import subprocess



class ENTRY(object):
    def list(self):
        """
        列出windows系统中的所有计划任务
        """
        try:
            result = subprocess.run(['schtasks', '/query', '/fo', 'LIST'], capture_output=True, text=True, encoding='utf-8')
            print(result.stdout)
        except Exception as e:
            print(f"Error: {e}")
        


def main() -> None:
    fire.Fire(ENTRY)