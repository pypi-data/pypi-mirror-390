

import fire
import subprocess
import win32com.client
from datetime import datetime
from .config import CONFIG


class ENTRY(object):
    def __init__(self):
        self.config = CONFIG()
        pass

    def list_from_tschm(self):
        """
        使用win32com模块列出windows系统中 任务计划程序当中的 \\tschm 目录下的所有任务
        显示任务名称、状态、下次运行时间和上次运行结果
        """
        try:
            scheduler = win32com.client.Dispatch('Schedule.Service')
            scheduler.Connect()
            
            # 获取 \tschm 文件夹
            try:
                tschmFolder = scheduler.GetFolder('\\tschm')
            except Exception:
                print("错误: 找不到 \\tschm 文件夹")
                print("提示: 请确保任务计划程序中存在 \\tschm 文件夹")
                return []
            
            tasks = tschmFolder.GetTasks(0)
            
            if tasks.Count == 0:
                print("\\tschm 文件夹中没有任务")
                return []
            
            print(f"\n找到 {tasks.Count} 个任务:\n")
            print("-" * 100)
            
            task_list = []
            for task in tasks:
                # 获取任务状态
                state_map = {
                    0: "未知",
                    1: "已禁用",
                    2: "已排队",
                    3: "就绪",
                    4: "正在运行"
                }
                state = state_map.get(task.State, "未知")
                
                # 获取上次运行结果
                last_result = task.LastTaskResult
                result_status = "成功" if last_result == 0 else f"失败(0x{last_result:X})"
                
                # 格式化下次运行时间
                next_run = task.NextRunTime
                try:
                    # 如果是有效的日期时间
                    if next_run and str(next_run) != "1899-12-30 00:00:00":
                        next_run_str = str(next_run)
                    else:
                        next_run_str = "未计划"
                except:
                    next_run_str = "未计划"
                
                task_info = {
                    "name": task.Name,
                    "state": state,
                    "next_run": next_run_str,
                    "last_result": result_status,
                    "enabled": task.Enabled
                }
                task_list.append(task_info)
                
                # 打印任务信息
                print(f"任务名称: {task.Name}")
                print(f"  状态: {state} | 启用: {'是' if task.Enabled else '否'}")
                print(f"  下次运行: {next_run_str}")
                print(f"  上次结果: {result_status}")
                print("-" * 100)
            
            return 

        except ImportError:
            print("错误: 请先安装pywin32模块")
            print("安装命令: pip install pywin32")
            return []
        except Exception as e:
            print(f"执行失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return []

    def create_task(self, name: str, script: str, schedule: str = "DAILY", time: str = "12:00"):
        """
        在任务计划程序的 \\tschm 目录下创建一个新的定时任务
        任务名称为 name
        执行的脚本为 script 
        schedule 可选值为 DAILY, WEEKLY, MONTHLY
        time 格式为 HH:MM (24小时制)
        """
        try:
            import win32com.client
            import os
            from datetime import datetime

            # 验证脚本文件是否存在
            if not os.path.isfile(script):
                print(f"错误: 脚本文件不存在: {script}")
                return False

            # 验证时间格式
            try:
                hour, minute = time.split(":")
                hour = int(hour)
                minute = int(minute)
                if not (0 <= hour <= 23 and 0 <= minute <= 59):
                    raise ValueError
            except:
                print(f"错误: 时间格式无效，应为 HH:MM (24小时制)")
                return False

            # 验证调度类型
            schedule_upper = schedule.upper()
            if schedule_upper not in ["DAILY", "WEEKLY", "MONTHLY"]:
                print(f"错误: 调度类型无效，应为 DAILY, WEEKLY 或 MONTHLY")
                return False

            scheduler = win32com.client.Dispatch('Schedule.Service')
            scheduler.Connect()
            
            # 获取 \tschm 文件夹
            try:
                tschmFolder = scheduler.GetFolder('\\tschm')
            except Exception:
                print("错误: 找不到 \\tschm 文件夹")
                print("提示: 请先运行 'init' 命令创建 \\tschm 文件夹")
                return False

            # 检查任务是否已存在
            try:
                existing_task = tschmFolder.GetTask(name)
                print(f"警告: 任务 '{name}' 已存在，将被覆盖")
                tschmFolder.DeleteTask(name, 0)
            except:
                pass  # 任务不存在，继续创建

            # 创建任务定义
            taskDef = scheduler.NewTask(0)
            
            # 设置注册信息
            regInfo = taskDef.RegistrationInfo
            regInfo.Description = f"由 tschm 创建的定时任务: {name}"
            regInfo.Author = "tschm"

            # 设置主体信息（以当前用户身份运行）
            principal = taskDef.Principal
            principal.LogonType = 3  # TASK_LOGON_INTERACTIVE_TOKEN

            # 设置任务设置
            settings = taskDef.Settings
            settings.Enabled = True
            settings.StartWhenAvailable = True
            settings.Hidden = False
            settings.DisallowStartIfOnBatteries = False
            settings.StopIfGoingOnBatteries = False

            # 创建触发器
            triggers = taskDef.Triggers
            trigger = triggers.Create(2)  # 2 = TASK_TRIGGER_DAILY
            
            # 设置触发器类型
            if schedule_upper == "DAILY":
                trigger.Id = "DailyTrigger"
                trigger.DaysInterval = 1
            elif schedule_upper == "WEEKLY":
                trigger = triggers.Create(3)  # 3 = TASK_TRIGGER_WEEKLY
                trigger.Id = "WeeklyTrigger"
                trigger.WeeksInterval = 1
                trigger.DaysOfWeek = 127  # 所有天 (1111111 in binary)
            elif schedule_upper == "MONTHLY":
                trigger = triggers.Create(4)  # 4 = TASK_TRIGGER_MONTHLY
                trigger.Id = "MonthlyTrigger"
                trigger.MonthsOfYear = 0xFFF  # 所有月份
                trigger.DaysOfMonth = 1  # 每月第一天

            # 设置开始时间
            start_time = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
            trigger.StartBoundary = start_time.strftime("%Y-%m-%dT%H:%M:%S")
            trigger.Enabled = True

            # 创建操作（执行脚本）
            actions = taskDef.Actions
            action = actions.Create(0)  # 0 = TASK_ACTION_EXEC
            
            # 获取脚本的绝对路径和扩展名
            script_abs = os.path.abspath(script)
            script_ext = os.path.splitext(script_abs)[1].lower()
            script_dir = os.path.dirname(script_abs)
            
            # 根据脚本类型设置执行程序
            if script_ext == '.py':
                action.Path = 'python'
                action.Arguments = f'"{script_abs}"'
            elif script_ext in ['.bat', '.cmd']:
                action.Path = 'cmd.exe'
                action.Arguments = f'/c "{script_abs}"'
            elif script_ext == '.ps1':
                action.Path = 'powershell.exe'
                action.Arguments = f'-ExecutionPolicy Bypass -File "{script_abs}"'
            else:
                # 直接执行
                action.Path = script_abs
                action.Arguments = ''
            
            action.WorkingDirectory = script_dir

            # 注册任务
            tschmFolder.RegisterTaskDefinition(
                name,
                taskDef,
                6,  # TASK_CREATE_OR_UPDATE
                '',  # 用户名（空表示当前用户）
                '',  # 密码
                3   # TASK_LOGON_INTERACTIVE_TOKEN
            )

            print(f"成功: 已创建任务 '{name}'")
            print(f"  脚本: {script_abs}")
            print(f"  调度: {schedule_upper}")
            print(f"  时间: {time}")
            return True

        except ImportError:
            print("错误: 请先安装pywin32模块")
            print("安装命令: pip install pywin32")
            return False
        except Exception as e:
            print(f"执行失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


    def delete_task(self, name: str):
        """
        删除任务计划程序中 \\tschm 目录下的指定任务
        任务名称为 name
        """
        try:
            import win32com.client

            scheduler = win32com.client.Dispatch('Schedule.Service')
            scheduler.Connect()
            
            # 获取 \tschm 文件夹
            try:
                tschmFolder = scheduler.GetFolder('\\tschm')
            except Exception:
                print("错误: 找不到 \\tschm 文件夹")
                print("提示: 请先运行 'init' 命令创建 \\tschm 文件夹")
                return False

            # 删除指定任务
            try:
                tschmFolder.DeleteTask(name, 0)
                print(f"成功: 已删除任务 '{name}'")
                return True
            except Exception:
                print(f"错误: 任务 '{name}' 不存在")
                return False

        except ImportError:
            print("错误: 请先安装pywin32模块")
            print("安装命令: pip install pywin32")
            return False
        except Exception as e:
            print(f"执行失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


def main() -> None:
    fire.Fire(ENTRY)