

import fire
import subprocess
import win32com.client
from datetime import datetime
from .config import CONFIG
import win32com.client
import os
from datetime import datetime

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
        except Exception as e:
            print(f"执行失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return []

    def add_task(self, name: str, script: str, schedule: str = "DAILY", time: str = "12:00"):
        """
        在任务计划程序的 \\tschm 目录下创建一个新的定时任务
        任务名称为 name
        执行的脚本为 script, 现在当前目录当中 寻找 script 文件
            如果当前目录当中存在 script文件 需要先把文件复制到 self.config._config_path 目录下 然后再添加 任务 并且支持 唤醒计算器去运行设置的任务
                文件复制过程中如果发现 self.config._config_path 目录下已经存在同名文件 则需要抛出文件重复提示 并结束操作
            如果当前目录当中不存在 script文件 则在 self.config._config_path 目录下寻找 script 文件
            如果找不到文件则抛出 找不到文件提示并结束操作
        schedule 可选值为 DAILY, WEEKLY, MONTHLY
        time 格式为 HH:MM (24小时制)
        """
        try:
            # 获取当前工作目录
            current_dir = os.getcwd()
            config_dir = os.path.dirname(self.config._config_path)
            
            # 确保配置目录存在
            if not os.path.exists(config_dir):
                os.makedirs(config_dir)
            
            # 确定脚本文件的最终路径
            script_path_in_current = os.path.join(current_dir, script)
            script_path_in_config = os.path.join(config_dir, script)
            final_script_path = None
            
            # 检查当前目录是否存在脚本文件
            if os.path.isfile(script_path_in_current):
                # 检查配置目录是否已存在同名文件
                if os.path.exists(script_path_in_config):
                    print(f"错误: 配置目录下已存在同名文件 '{script}'")
                    print(f"路径: {script_path_in_config}")
                    return False
                
                # 复制文件到配置目录
                try:
                    import shutil
                    shutil.copy2(script_path_in_current, script_path_in_config)
                    print(f"已将脚本复制到配置目录: {script_path_in_config}")
                    final_script_path = script_path_in_config
                except Exception as e:
                    print(f"错误: 复制文件失败 - {str(e)}")
                    return False
            else:
                # 当前目录不存在，检查配置目录
                if os.path.isfile(script_path_in_config):
                    final_script_path = script_path_in_config
                    print(f"使用配置目录中的脚本: {script_path_in_config}")
                else:
                    print(f"错误: 找不到脚本文件 '{script}'")
                    print(f"已检查路径:")
                    print(f"  - {script_path_in_current}")
                    print(f"  - {script_path_in_config}")
                    return False
            
            # 验证时间格式
            try:
                hour, minute = time.split(":")
                hour = int(hour)
                minute = int(minute)
                if not (0 <= hour <= 23 and 0 <= minute <= 59):
                    raise ValueError
            except:
                print(f"错误: 时间格式无效 '{time}'，应为 HH:MM (24小时制)")
                return False
            
            # 验证 schedule 参数
            schedule = schedule.upper()
            if schedule not in ["DAILY", "WEEKLY", "MONTHLY"]:
                print(f"错误: schedule 参数无效 '{schedule}'，可选值为 DAILY, WEEKLY, MONTHLY")
                return False
            
            # 创建任务计划
            scheduler = win32com.client.Dispatch('Schedule.Service')
            scheduler.Connect()
            
            # 获取 \tschm 文件夹
            try:
                tschmFolder = scheduler.GetFolder('\\tschm')
            except Exception:
                print("错误: 找不到 \\tschm 文件夹")
                print("提示: 请先运行 'init' 命令创建 \\tschm 文件夹")
                return False
            
            # 创建任务定义
            taskDef = scheduler.NewTask(0)
            
            # 设置注册信息
            regInfo = taskDef.RegistrationInfo
            regInfo.Description = f"由 tschm 创建的定时任务: {name}"
            regInfo.Author = "tschm"
            
            # 设置主体（运行账户）
            principal = taskDef.Principal
            principal.LogonType = 3  # TASK_LOGON_INTERACTIVE_TOKEN
            
            # 设置任务设置
            settings = taskDef.Settings
            settings.Enabled = True
            settings.StartWhenAvailable = True
            settings.Hidden = False
            settings.WakeToRun = True  # 唤醒计算机以运行此任务
            
            # 创建触发器
            triggers = taskDef.Triggers
            trigger = triggers.Create(2)  # 2 = TASK_TRIGGER_DAILY
            
            # 设置开始时间
            start_time = datetime.now().replace(hour=hour, minute=minute, second=0, microsecond=0)
            trigger.StartBoundary = start_time.strftime("%Y-%m-%dT%H:%M:%S")
            
            # 根据 schedule 设置触发器
            if schedule == "DAILY":
                trigger.DaysInterval = 1
            elif schedule == "WEEKLY":
                trigger = triggers.Create(3)  # 3 = TASK_TRIGGER_WEEKLY
                trigger.StartBoundary = start_time.strftime("%Y-%m-%dT%H:%M:%S")
                trigger.WeeksInterval = 1
                trigger.DaysOfWeek = 127  # 每天 (1111111 in binary)
            elif schedule == "MONTHLY":
                trigger = triggers.Create(4)  # 4 = TASK_TRIGGER_MONTHLY
                trigger.StartBoundary = start_time.strftime("%Y-%m-%dT%H:%M:%S")
                trigger.MonthsOfYear = 0xFFF  # 所有月份
                trigger.DaysOfMonth = 1  # 每月第一天
            
            # 创建操作（执行脚本）
            actions = taskDef.Actions
            action = actions.Create(0)  # 0 = TASK_ACTION_EXEC
            
            # 根据脚本扩展名确定执行方式
            script_ext = os.path.splitext(final_script_path)[1].lower()
            if script_ext == '.ps1':
                action.Path = "powershell.exe"
                action.Arguments = f'-ExecutionPolicy Bypass -File "{final_script_path}"'
            elif script_ext in ['.bat', '.cmd']:
                action.Path = final_script_path
            else:
                # 默认使用 powershell 执行
                action.Path = "powershell.exe"
                action.Arguments = f'-ExecutionPolicy Bypass -File "{final_script_path}"'
            
            # 注册任务
            tschmFolder.RegisterTaskDefinition(
                name,
                taskDef,
                6,  # TASK_CREATE_OR_UPDATE
                None,  # 使用当前用户
                None,  # 不需要密码
                3,  # TASK_LOGON_INTERACTIVE_TOKEN
                ""
            )
            
            print(f"成功: 已创建任务 '{name}'")
            print(f"  脚本: {final_script_path}")
            print(f"  计划: {schedule}")
            print(f"  时间: {time}")
            print(f"  唤醒计算机: 是")
            return True
            
        except Exception as e:
            print(f"执行失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


    def del_task(self, name: str):
        """
        删除任务计划程序中 \\tschm 目录下的指定任务
        任务名称为 name
        """
        try:
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
            
        except Exception as e:
            print(f"执行失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False


def main() -> None:
    fire.Fire(ENTRY)