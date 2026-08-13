resume_skills = {"Python","Git","RAG","FastAPI"}
job_skills = {"Pyhton","Git","RAG","FastAPI","Docker","SQL"}

matched_skills = resume_skills & job_skills
missing_skills = job_skills - resume_skills

if job_skills:
    match_score = len(matched_skills) / len(job_skills) *100
else:
    match_score = 0
    print("提示: 职位没有设置技能要求")

print("匹配技能:",matched_skills)
print("缺失技能:",missing_skills)
print("匹配分数:",round(match_score,1),"%")

if match_score >=80:
    risk_level = "low"
elif match_score >=50:
    risk_level = "medium"
else:
    risk_level = "high"

print("风险等级:",risk_level)