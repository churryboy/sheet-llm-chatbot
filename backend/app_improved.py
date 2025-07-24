import os
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from json_unicode import jsonify_unicode
from google.oauth2 import service_account
from googleapiclient.discovery import build
from anthropic import Anthropic
from dotenv import load_dotenv
import json
import requests
import csv
import io

# Load the existing app.py content
from app import *

def create_prompt_improved(user_question, sheet_data, search_results=None):
    """개선된 프롬프트 생성 함수 - 중학생 카운팅에 특화"""
    prompt_parts = []
    
    # 1. 구글 시트 데이터 섹션
    data_str = ""
    if sheet_data:
        # 중학생 관련 질문인 경우 특별 처리
        if "중학생" in user_question or "중1" in user_question or "중2" in user_question or "중3" in user_question:
            data_str = "=== 구글 시트 데이터 (학생 정보) ===\n\n"
            
            # 중학생만 필터링
            middle_school_students = []
            for row in sheet_data:
                grade = row.get('현재 학년이 어떻게 되나요?', '').strip()
                if grade in ['중1', '중2', '중3']:
                    middle_school_students.append(row)
            
            # 전체 개요
            data_str += f"전체 데이터: {len(sheet_data)}명\n"
            data_str += f"중학생 데이터: {len(middle_school_students)}명\n\n"
            
            # 학년별 통계
            grade_counts = {'중1': 0, '중2': 0, '중3': 0}
            for student in middle_school_students:
                grade = student.get('현재 학년이 어떻게 되나요?', '').strip()
                if grade in grade_counts:
                    grade_counts[grade] += 1
            
            data_str += "학년별 분포:\n"
            for grade, count in grade_counts.items():
                data_str += f"- {grade}: {count}명\n"
            data_str += "\n"
            
            # 중요 필드만 선택하여 표시
            important_fields = [
                '이름을 적어주세요',
                '현재 학년이 어떻게 되나요?',
                '성별이 어떻게 되나요?',
                '현재 거주중인 지역이 어디인가요? ',
                '현재 다니고 있는 학교 이름을 적어주세요',
                '다음 중 가장 *자신없는, 힘들어하는* 과목을 선택해주세요',
                '다음 중, 공부하는 가장 큰 목적은 무엇인가요?'
            ]
            
            # 중학생 데이터를 간결하게 표시
            data_str += "=== 중학생 상세 정보 ===\n\n"
            for i, student in enumerate(middle_school_students, 1):
                data_str += f"[학생 {i}]\n"
                for field in important_fields:
                    if field in student and student[field]:
                        data_str += f"- {field}: {student[field]}\n"
                data_str += "\n"
                
                # 토큰 제한을 고려하여 최대 30명까지만 상세 정보 표시
                if i >= 30:
                    data_str += f"... 그 외 {len(middle_school_students) - 30}명의 중학생 데이터가 더 있습니다.\n"
                    break
        
        else:
            # 일반적인 질문의 경우 기존 방식 사용하되 개선
            data_str = "=== 구글 시트 데이터 ===\n\n"
            headers = list(sheet_data[0].keys())
            
            # 데이터 요약 정보
            data_str += f"총 {len(sheet_data)}개의 데이터 행\n"
            data_str += f"컬럼 수: {len(headers)}개\n\n"
            
            # 헤더만 표시
            data_str += "데이터 컬럼:\n"
            for i, header in enumerate(headers[:20]):  # 처음 20개 컬럼만
                data_str += f"{i+1}. {header}\n"
            if len(headers) > 20:
                data_str += f"... 그 외 {len(headers) - 20}개 컬럼\n"
            data_str += "\n"
            
            # 처음 10개 행만 샘플로 표시
            data_str += "데이터 샘플 (처음 10행):\n"
            for i in range(min(10, len(sheet_data))):
                data_str += f"\n행 {i+1}:\n"
                for header in headers[:5]:  # 각 행에서 처음 5개 필드만
                    value = str(sheet_data[i].get(header, ''))
                    if value:
                        # 긴 텍스트는 축약
                        if len(value) > 100:
                            value = value[:100] + "..."
                        data_str += f"  {header}: {value}\n"
    else:
        data_str = "=== 구글 시트 데이터 ===\n데이터가 없습니다.\n"
    
    prompt_parts.append(data_str)
    
    # 2. 웹 검색 결과 섹션 (기존과 동일)
    if search_results:
        search_str = "\n\n=== 웹 검색 결과 ===\n\n"
        for idx, result in enumerate(search_results, 1):
            search_str += f"[{idx}] {result['title']}\n"
            search_str += f"   출처: {result['displayLink']}\n"
            search_str += f"   요약: {result['snippet']}\n"
            search_str += f"   링크: {result['link']}\n\n"
        prompt_parts.append(search_str)
    
    # 3. 전체 프롬프트 조합
    full_prompt = "\n".join(prompt_parts)
    
    # 4. 질문과 주의사항 추가
    if "중학생" in user_question:
        instructions = f"""

위 데이터를 참고하여 다음 질문에 답해주세요:
질문: {user_question}

주의사항:
1. 제공된 데이터에 따르면 중학생은 총 {len([r for r in sheet_data if r.get('현재 학년이 어떻게 되나요?', '') in ['중1', '중2', '중3']])}명입니다.
2. 학년별 인원수를 정확히 계산하여 답변해주세요.
3. 데이터를 기반으로 정확한 정보를 제공하고, 필요한 경우 추가적인 분석이나 인사이트도 제공하세요.
4. 답변은 친절하고 상세하게 작성해주세요.
"""
    else:
        instructions = f"""

위 데이터를 참고하여 다음 질문에 답해주세요:
질문: {user_question}

주의사항:
1. 데이터에 인터뷰 스크립트나 대화 내용이 있다면, 해당 내용을 꼼꼼히 분석하여 답변하세요.
2. 사람의 이름이 언급되면, 해당 인물과 관련된 모든 정보를 종합하여 답변하세요.
3. 답변은 친절하고 상세하게 작성해주세요.
4. 데이터를 기반으로 정확한 정보를 제공하고, 필요한 경우 추가적인 분석이나 인사이트도 제공하세요.
"""
    
    return full_prompt + instructions
