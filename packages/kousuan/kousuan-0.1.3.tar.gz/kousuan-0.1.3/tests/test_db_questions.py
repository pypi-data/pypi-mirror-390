import unittest
import sqlite3
import sys
import os
import json
import traceback
from datetime import datetime
from fractions import Fraction

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from kousuan.core import calculate, resolve

question_db_file = "/Users/liuliandong/workspace/databank/ai_pal/questions/kousuan_data.db"
record_db_file = "./kousuan_results.db"
log_file = "./logs/kousuan_results.log"
error_log_file = "./logs/kousuan_errors.log"

class Recorder:
    def __init__(self, db_file: str):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()
        self.init_record_table()
    
    def init_record_table(self):
        """初始化结果记录表"""
        create_table_query = """
        CREATE TABLE IF NOT EXISTS kousuan_question_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id INTEGER UNIQUE,
            body TEXT,
            answers TEXT,
            passed BOOLEAN,
            result TEXT,
            knowledge_name TEXT,
            created_at TEXT,
            FOREIGN KEY (question_id) REFERENCES kousuan_questions(id)
        )
        """
        self.cursor.execute(create_table_query)
        
        # 创建索引以提高查询性能
        self.cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_question_id ON kousuan_question_results(question_id)
        """)
        
        self.connection.commit()

    def record_result(self, question_id: int, body: str, answers: str, passed: bool, 
                     result: str, knowledge_name: str):
        """记录题目的计算结果，存在则覆盖"""
        current_time = datetime.now().isoformat()
        
        # 使用 INSERT OR REPLACE 实现去重复和覆盖
        insert_query = """
        INSERT OR REPLACE INTO kousuan_question_results 
        (question_id, body, answers, passed, result, knowledge_name, created_at) 
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        self.cursor.execute(insert_query, (question_id, body, answers, passed, 
                                         result, knowledge_name, current_time))
        self.connection.commit()

    def close(self):
        self.connection.close()

class KnowledgePointTester:
    def __init__(self):
        self.connection = sqlite3.connect(question_db_file)
        self.cursor = self.connection.cursor()
        self.recorder = Recorder(record_db_file)

    def get_knowledge_points_stats(self):
        """获取所有知识点的统计信息，按题目数量降序排列"""
        query = """
        SELECT knowledge_name, COUNT(*) as question_count 
        FROM questions 
        GROUP BY knowledge_name 
        ORDER BY question_count DESC
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def query_questions_by_knowledge(self, knowledge_name: str, page: int = 1, page_size: int = 50):
        """根据知识点分页查询题目"""
        offset = (page - 1) * page_size
        query = """
        SELECT id, body, answers, knowledge_name 
        FROM questions 
        WHERE knowledge_name = ? 
        ORDER BY id 
        LIMIT ? OFFSET ?
        """
        self.cursor.execute(query, (knowledge_name, page_size, offset))
        return self.cursor.fetchall()

    def get_total_questions_by_knowledge(self, knowledge_name: str):
        """获取指定知识点的总题目数"""
        query = "SELECT COUNT(*) FROM questions WHERE knowledge_name = ?"
        self.cursor.execute(query, (knowledge_name,))
        return self.cursor.fetchone()[0]

    def log_result(self, knowledge_name: str, question_id: int, body: str, answers: str, passed: bool, 
                   algorithm_name: str, result_value: str, description: str):
        """记录结果到日志文件"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = (
            f"[{timestamp}] 知识点:{knowledge_name} | ID:{question_id} | 题目:{body} | "
            f"期望答案:{answers} | 通过:{passed} | "
            f"算法:{algorithm_name} | 结果:{result_value} | 描述:{description}\n"
        )
        log_file = f"logs/{knowledge_name}_kousuan_results.log"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)

    def log_error(self, knowledge_name: str, question_id: int, body: str, error_msg: str):
        """记录异常到错误日志文件"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_entry = f"[{timestamp}] 知识点:{knowledge_name} | ID:{question_id} | 题目:{body} | 错误:{error_msg}\n"
        
        with open(error_log_file, "a", encoding="utf-8") as f:
            f.write(error_entry)

    def test_knowledge_point(self, knowledge_name: str):
        """测试指定知识点的所有题目"""
        total_questions = self.get_total_questions_by_knowledge(knowledge_name)
        total_pages = (total_questions + 49) // 50  # 向上取整
        total_errors = 0

        ## 删除知识点日志文件
        log_file = f"logs/{knowledge_name}_kousuan_results.log"
        if os.path.exists(log_file):
            os.remove(log_file)
        
        print(f"\n开始测试知识点: {knowledge_name} (共{total_questions}题, {total_pages}页)")
        
        for page in range(1, total_pages + 1):
            print(f"  处理第{page}页...")
            if total_errors >= 20:
                print(f"    错误数达到20，停止测试该知识点")
                break
            questions = self.query_questions_by_knowledge(knowledge_name, page)
            
            for question in questions:
                q_id, body, answers, knowledge_name_db = question
                try:
                    r = self.process_single_question(q_id, body, answers, knowledge_name_db)
                    if r and r.get('passed') is False:
                        total_errors += 1
                except Exception as e:
                    total_errors += 1
                    error_msg = f"处理异常: {str(e)}\n{traceback.format_exc()}"
                    self.log_error(knowledge_name, q_id, body, error_msg)
                    print(f"    题目ID {q_id} 处理异常: {str(e)}")

    def process_single_question(self, q_id: int, body: str, answers: str, knowledge_name: str) -> dict | None:
        """处理单个题目"""
        try:
            results = resolve(body)
            
            # 解析期望答案
            try:
                expected_answers = json.loads(answers)
            except:
                expected_answers = [answers]  # 如果不是JSON格式，直接作为单个答案
            
            # 获取计算结果
            result_values = []
            algorithm_name = "无"
            result_value = "无结果"
            description = "无描述"
            
            if results and len(results) > 0:
                first_result = results[0]
                algorithm_name = first_result.get('name', '未知算法')
                result_value = str(first_result.get('result', ''))
                description = first_result.get('description', '')
                result_values = [str(res.get('latexResult', '') or res.get('result', '')) for res in results]
            
            # 检查是否通过
            passed = any(str(ans) in result_values for ans in expected_answers)
            
            # 记录到数据库
            db_result = {
                'name': algorithm_name,
                'result': result_value,
                'description': description
            }
            self.recorder.record_result(
                question_id=q_id,
                body=body,
                answers=answers,
                passed=passed,
                result=json.dumps(db_result, ensure_ascii=False),
                knowledge_name=knowledge_name
            )
            
            # 记录到日志文件
            if not passed:
                self.log_result(knowledge_name, q_id, body, answers, passed, algorithm_name, 
                            result_value, description)
            
            if not passed:
                print(f"    未通过 ID:{q_id} 期望:{expected_answers} 实际:{result_values}")

            return {
                'question_id': q_id,
                'body': body,
                'answers': answers,
                'result_values': result_values,
                'knowledge_name': knowledge_name,
                'passed': passed
            }
                
        except Exception as e:
            error_msg = f"计算异常: {str(e)}"
            self.log_error(q_id, body, error_msg)
            
            # 记录失败结果到数据库
            self.recorder.record_result(
                question_id=q_id,
                body=body,
                answers=answers,
                passed=False,
                result=json.dumps({"error": error_msg}, ensure_ascii=False),
                knowledge_name=knowledge_name
            )

    def run_all_tests(self):
        """运行所有知识点的测试"""
        try:
            # 获取知识点统计
            knowledge_stats = self.get_knowledge_points_stats()
            print("知识点统计 (按题目数量降序):")
            for knowledge_name, count in knowledge_stats:
                print(f"  {knowledge_name}: {count}题")
            
            # 按题目数量从多到少测试各个知识点
            for knowledge_name, count in knowledge_stats:
                try:
                    self.test_knowledge_point(knowledge_name)
                except Exception as e:
                    error_msg = f"测试知识点'{knowledge_name}'时发生异常: {str(e)}"
                    print(error_msg)
                    with open(error_log_file, "a", encoding="utf-8") as f:
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        f.write(f"[{timestamp}] {error_msg}\n")
            
            print(f"\n所有测试完成!")
            print(f"结果已保存到: {record_db_file}")
            print(f"详细日志: {log_file}")
            print(f"错误日志: {error_log_file}")
            
        finally:
            self.close()

    def close(self):
        """关闭数据库连接"""
        self.connection.close()
        self.recorder.close()

def main():
    """主函数"""
    # 创建日志文件头部信息
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"\n{'='*80}\n")
        f.write(f"测试开始时间: {timestamp}\n")
        f.write(f"{'='*80}\n")
    
    # 运行测试
    tester = KnowledgePointTester()
    # tester.run_all_tests()
    tester.test_knowledge_point("公顷和平方千米")

if __name__ == "__main__":
    main()