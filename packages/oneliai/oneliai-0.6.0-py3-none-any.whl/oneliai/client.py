import requests
import asyncio
import uuid
import logging
import os
import pymysql
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, date, time, timedelta
import decimal
URL="https://apis.oneli.chat"
# URL="http://localhost:8085"

appurl="http://localhost:3000"
class AIClient:
    def __init__(self, client_id, client_secret, base_url=f'{URL}/v1/strategy'):
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = base_url
        self.access_token = self._get_access_token()

    def _get_access_token(self):
        response = requests.post(
            f'{self.base_url}/auth/token',
            json={
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'grant_type': 'client_credentials'
            }
        )
        if response.status_code == 200:
            return response.json().get('access_token')
        else:
            raise Exception('Failed to get access token')

    def generate_response(self, question,template_id, variables):
        response = requests.post(
            f'{self.base_url}/dynamic-response',
            json={
                'question':question,
                'template_id': template_id,
                'variables': variables
            },
            headers={'Authorization': f'Bearer {self.access_token}'}
        )
        if response.status_code == 200:
            return response.json().get('response')
        else:
            return response.json()
            # raise Exception('Failed to generate response')

    def query_data(self, arg, template_id):
        response = requests.post(
            f'{self.base_url}/query-data',
            json={
                'arg': arg,
                'template_id': template_id
            },
            headers={'Authorization': f'Bearer {self.access_token}'}
        )
        if response.status_code == 200:
            return response.json()
        else:
            res=response.json()
            raise Exception(res['error'])
        

    def query_intention(self, question):
        response = requests.post(
            f'{self.base_url}/query-intention',
            json={
                'question': question
             
            },
            headers={'Authorization': f'Bearer {self.access_token}'}
        )
        if response.status_code == 200:
            return response.json()
        else:
            
            raise Exception('Failed to start intention query')
        
    def voc(self,productname,text):
        response = requests.post(
            f'{self.base_url}/voc',
            json={
                'productname': productname,
                'text':text
            },
            headers={'Authorization': f'Bearer {self.access_token}'}
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception('Failed to start voc ')
        

    def spec(self,asin):
        response = requests.post(
            f'{self.base_url}/spec', 
            json={
                'asin': asin
               
            },
            headers={'Authorization': f'Bearer {self.access_token}'}
        )
        if response.status_code == 200:
            return response.json()
        else:
            res=response.json()
            raise Exception(f'Failed to start voc,reason:{res["error"]}')

     #选品建议   
    def suggestion(self, selected_products):
        response = requests.post(
            f'{self.base_url}/suggestion',
            json={
                "final_selected_products": selected_products
           
            },
            headers={'Authorization': f'Bearer {self.access_token}'}
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception('Failed to start suggestion')
        
    async def competitor_analysis(self,missionid="",asins=[]):
        if not missionid:  # Check if missionid is empty
           missionid = str(uuid.uuid4())  # Generate a random UUID
        
        task_id = await self.get_competitive_data(missionid,asins)
       
        # logging.info(task_id)
    
        if task_id:
            
            task = await self.check_task_status(task_id)
            
            
            if task['result']['code'] == 200:
                
                ret=await self.analysis_details(missionid)
                return ret
            else:
                return {'code': 400, 'data': None, 'msg':task['result']['msg']}
        
       
    async def analysis_details(self,missionid):
        response = requests.post(
            f'{URL}/v1/conv/analysis/getid', 
            json={
                'missionid': missionid
               
            },
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception('Failed to start analysis')

        
    async def get_competitive_data(self,missionid,asins=[]):
        print(2)
        response = requests.post(
                f'{self.base_url}/competitor_analysis',
                json={
                    "asins": asins,
                    "missionid":missionid
            
                },
                headers={'Authorization': f'Bearer {self.access_token}'}
            )
        
        if response.status_code == 200:
        
           result=response.json()
              
           return result['data']['task_id']
        else:
            raise Exception('Failed to request get_competitive_data')
     
    

    #获取所有asins
    async def productList(self,missionid):
        data=await self.get_token()
        print(data['token'])
        response = requests.post(
            f"{URL}/v1/agent/productList",
            json={
                'missionid':missionid
            },
            headers={'Authorization': f"Bearer {data['token']}"}
        )

        print(response)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception('Failed to request task_status')



    async def getTaskStatus(self,taskId):
        data=await self.get_token()
        print(data['token'])
        response =requests.get(f"{URL}/v1/task/task_status/{taskId}",
                                headers={'Authorization': f"Bearer {data['token']}"})
        print(response.json())
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception('Failed to request task_status')
        
    async def check_task_status(self,task_id):
        print(3)
        
        while True:
            try:
                
                response = await self.getTaskStatus(task_id)
                logging.info(response)
                status = response.get('status')
                logging.info(f"Task status: {status}")
                print("------------------")
                if status == "SUCCESS":
                    return {"status": "SUCCESS", "result": response.get('result')}
                    
            except Exception as error:
                logging.error(f"Error checking task status: {error}")
            
            await asyncio.sleep(1)  # Sleep for 1 second
     

    async def getGoodinfofromAmazon(self, asins,filename=None):
        if filename:
            locafile,filename=self.upload_file(filename)
            print(filename)
        
        
            response=self.create_asin_mission(locafile,filename)
            asins=response['asins']

        response = requests.post(
            f'{appurl}/api/run-task',
            json={
                "type": "asin",
                "data":{"asins": asins}
            
            },
        
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception('Failed to run task')
        
    async def getAsinfromAmazon(self,title,keywords):
        missionid = str(uuid.uuid4()) 
        await self.update_mission("app_"+missionid, title,keywords)
        response = requests.post(
            f'{appurl}/api/run-task',
            json={
                "type": "list",
                "data":{"keywords":keywords,"missionid":"app_"+missionid}
            
            },
        
        )


        # if response.status_code == 202:
        # task_id = response.json()['task_id']
        # print(f"Task started with ID: {task_id}")
        # return task_id
        #print(response)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception('Failed to run task')

        
    def upload_file(self,file_path):
        url =f"{URL}/v1/task/upload"
        file_name = os.path.basename(file_path)
        with open(file_path, 'rb') as f:
            files = {'file': (file_name, f)}
            response = requests.post(url, files=files)
        
        if response.status_code == 200:
            data = response.json()
            print(f"Uploaded filename: {data['filename']}")
            return file_name,data['filename']
        else:
            print(f"Upload failed: {response.text}")
            return None


    async def create_asin_mission(self,locafile,filename):
        # Start ASIN extraction process
        task_id = await self.create_asin_mission_api(filename)
        
        if task_id:
            task = await self.check_task_status(task_id)
            
            if task["status"] == "SUCCESS" and task["result"]["code"] == 200:
                missionid = task["result"]["missionid"]
                
                # Generate report title using AI
                gentitle_prompt = f"""
                以下是选品报告标题的关键要素
                今天是{datetime.now()}
                用户了提交了asin 列表,文件名称为{locafile}
                请生成亚马逊选品分析报告的标题
                """
                response_title = await self.call_ai_api([{"role": "user", "content": gentitle_prompt}])
                title = response_title["data"]
                
                # Update mission with generated title
                task_res = await self.update_mission(missionid, title, "无需关键词")
                
                if task_res["code"] == 200:
                    # Get ASIN list for the mission
                    res = await self.get_asin_list(missionid)
                    
                    if res["code"] == 200:
                        asinlist = res["data"]
                        asins = [item["asin"] for item in asinlist]
                        return {"missionid": missionid, "asins": asins}
        
        # Return None if any step fails
        return None
    


    # Example implementations of the required service functions
    async def create_asin_mission_api(self,filename: str) -> str:
     
        response = requests.post(
            f"{URL}/task/start_task",
            json={
                'name':"create_asin_mission",
                'data': {"file_name":filename},
            }
           
        )
        """Mock implementation - replace with actual API call"""
        if response.status_code == 200:
            res=response.json()
            return res['task_id']
        else:
            raise Exception('Failed to request task_status')
        

    # async def check_task_status(self,task_id: str) -> dict:
    #     response =requests.get(f"{URL}/task/task_status/{task_id}")
    #     if response.status_code == 200:
    #         ret= response.json()
    #         """Mock implementation - replace with actual status check"""
    #         return {
    #             "status": ret["status"],
    #             "result": {
    #                 "code": 200,
    #                 "missionid": ret["result"]["missionid"]
    #             }
    #         }
    #     else:
    #         raise Exception('Failed to request task_status')
    
    async def get_token(self):
        
        response =requests.get(f"{appurl}/api/gettoken")
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception('Failed to request task_status')
        # response =requests.get(f"{URL}/system/sdklogin")
        # if response.status_code == 200:
        #     return response.json()
        # else:
        #     raise Exception('Failed to request task_status')

    async def call_ai_api(self,messages,tools):
        data=await self.get_token()
        print(data)
        response = requests.post(
            f"{URL}/agent/fn",
            json={"tools":tools,"messages":messages},
            headers={'Authorization': f"Bearer {data['token']}"}
        )

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception('Failed to request task_status')
        

    async def update_mission(self,missionid: str, title: str, keywords: str) :
        data=await self.get_token()
        print(data['token'])
        response = requests.post(
            f"{URL}/v1/agent/intertMissioinlist",
            json={
                'task_id':missionid,
                'report_title': title,
                'keywords': keywords,
                'task_status':'In Progress',
                'task_status_description':'数据采集任务开始'
            },
            headers={'Authorization': f"Bearer {data['token']}"}
        )

        print(response)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception('Failed to request task_status')
        

    async def get_asin_list(self,missionid: str):
        response = requests.post(
            f"{URL}/conv/getid",
            json={
                'missionid':missionid}
           )

        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception('Failed to request task_status')
        

        


    async def getallpageData(self,missionid: str) :
        data=await self.get_token()
        print(data['token'])
        response = requests.post(
            f"{URL}/v1/agent/test/getallpageData",
            json={
                'missionid':missionid
            },
            headers={'Authorization': f"Bearer {data['token']}"}
        )

        print(response)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception('Failed to request task_status')
        
    #保存数据到云
    async def CloudStorage(self,input_data:Any,config: dict={}) :
        data=await self.get_token()
        missionid=str(uuid.uuid4())  # Generate a random UUID
        response = requests.post(
            f"{URL}/v1/conv/analysis/save",
            json={
                'id':missionid,
                'data':input_data
            },
            headers={'Authorization': f"Bearer {data['token']}"}
        )

        
        if response.status_code == 200:
            return  {"missionid": missionid, "msg":"已经保存完成"}
        else:
            raise Exception('Failed to request task_status')
        


    #读取数据库
    async def Database(self,input_data: str, config: dict={}) -> Optional[object]:
        """
        执行 MySQL 查询并返回包含 database-source 属性的对象
        只支持 SELECT 查询，自动限制最多1000条数据
        """
        # 从 config 中获取参数
        sql_query = config.get('query', '')
        connection_string = config.get('connectionString', '')
        
        if not sql_query:
            print("SQL 查询语句不能为空")
            return None
            
        if not connection_string:
            print("数据库连接字符串不能为空")
            return None

        # 检查是否只支持 SELECT 查询
        sql_upper = sql_query.strip().upper()
        if not sql_upper.startswith('SELECT'):
            print("只支持 SELECT 查询语句")
            return None

        # 解析连接字符串
        config_dict = {}
        try:
            for param in connection_string.split(';'):
                if '=' in param:
                    key, value = param.split('=', 1)
                    config_dict[key.strip()] = value.strip()
        except Exception as e:
            print(f"连接字符串解析失败: {e}")
            return None

        # 建立数据库连接
        connection = None
        try:
            connection = pymysql.connect(
                host=config_dict.get('host', 'localhost'),
                port=int(config_dict.get('port', 3306)),
                user=config_dict.get('user', ''),
                password=config_dict.get('password', ''),
                database=config_dict.get('database', ''),
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor
            )
            
            # 执行查询
            with connection.cursor() as cursor:
                # 检查查询是否已经有 LIMIT 子句
                if 'LIMIT' not in sql_upper:
                    # 如果没有 LIMIT，自动添加 LIMIT 1000
                    modified_query = sql_query.rstrip(';') + ' LIMIT 1000'
                    print(f"自动添加 LIMIT 1000，执行查询: {modified_query}")
                    cursor.execute(modified_query)
                else:
                    # 如果已经有 LIMIT，检查是否超过1000条
                    # 提取 LIMIT 后面的数字
                    limit_index = sql_upper.find('LIMIT')
                    limit_part = sql_upper[limit_index:].split()
                    
                    if len(limit_part) >= 2:
                        try:
                            limit_value = int(limit_part[1])
                            if limit_value > 1000:
                                # 如果限制超过1000，修改为1000
                                original_limit = f"LIMIT {limit_value}"
                                new_limit = "LIMIT 1000"
                                modified_query = sql_query.replace(original_limit, new_limit)
                                print(f"限制条数从 {limit_value} 改为 1000，执行查询: {modified_query}")
                                cursor.execute(modified_query)
                            else:
                                # 如果限制在1000以内，直接执行
                                cursor.execute(sql_query)
                        except ValueError:
                            # 如果 LIMIT 参数不是数字，使用默认查询
                            cursor.execute(sql_query)
                    else:
                        # 如果 LIMIT 格式不正确，使用默认查询
                        cursor.execute(sql_query)
                
                result = cursor.fetchall()
                
                # 检查实际返回的数据条数
                actual_count = len(result)
                if actual_count == 1000:
                    print("警告：查询结果已达到1000条限制，可能有不完整数据")
                
                # JSON 序列化器
                def json_serializer(obj):
                    """支持多种数据类型的 JSON 序列化器"""
                    if isinstance(obj, (datetime, date)):
                        return obj.isoformat()
                    elif isinstance(obj, decimal.Decimal):
                        return float(obj)
                    elif isinstance(obj, (bytes, bytearray)):
                        return obj.decode('utf-8', errors='ignore')
                    elif isinstance(obj, time):
                        return obj.isoformat()
                    elif isinstance(obj, timedelta):
                        return str(obj)
                    else:
                        return str(obj)
                
                # 转换为 JSON
                json_result = json.dumps(result, ensure_ascii=False, default=json_serializer, indent=2)
                
                # 返回包含 database-source 属性的对象
                class DatabaseResult:
                    def __init__(self, result):
                        self.database_source = result
                
                return DatabaseResult(json_result)
                
        except pymysql.Error as e:
            print(f"数据库操作失败: {e}")
            return None
        except Exception as e:
            print(f"其他错误: {e}")
            return None
        finally:
            # 确保连接被关闭
            if connection:
                connection.close()


        
        

    
            
        
    
 