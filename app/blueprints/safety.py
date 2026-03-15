from flask import Blueprint, render_template

from app.utils.auth import login_required

bp = Blueprint("safety", __name__)


@bp.route("/safety/regulations")
@login_required
def regulations():
    standards = [
        {
            "code": "GB 26860-2011",
            "name": "电力安全工作规程（发电厂和变电站电气部分）",
            "level": "国家标准",
            "status": "现行有效",
            "version": "2011 版",
            "scope": "倒闸操作、停送电、现场作业组织",
            "keywords": ["倒闸操作", "工作票", "安全措施"],
            "updated_at": "2026-03-01",
            "owner": "周海峰",
            "department": "安全监督部",
        },
        {
            "code": "GB/T 13869-2017",
            "name": "用电安全导则",
            "level": "国家标准",
            "status": "重点推荐",
            "version": "2017 版",
            "scope": "日常用电、人员防护、设备接地",
            "keywords": ["触电预防", "接地", "绝缘"],
            "updated_at": "2026-02-18",
            "owner": "刘娜",
            "department": "设备管理部",
        },
        {
            "code": "DL 409-2021",
            "name": "电业安全工作规程（电力线路部分）",
            "level": "行业标准",
            "status": "待复核",
            "version": "2021 版",
            "scope": "输配电线路检修与高处作业",
            "keywords": ["线路检修", "高空作业", "验电"],
            "updated_at": "2026-03-09",
            "owner": "孙立群",
            "department": "运行检修中心",
        },
    ]
    return render_template("safety_regulations.html", standards=standards)


@bp.route("/safety/hazards")
@login_required
def hazards():
    summary = {
        "open": 18,
        "overdue": 5,
        "closed": 64,
        "high_risk": 7,
    }
    hazards = [
        {
            "ticket_no": "YH-202603-018",
            "title": "配电柜二次侧接线标识缺失",
            "location": "1 号变配电室",
            "level": "中风险",
            "owner": "王建国",
            "deadline": "2026-03-18",
            "status": "待整改",
            "measure": "补齐标识并复核图纸一致性",
            "source": "巡检发现",
        },
        {
            "ticket_no": "YH-202603-014",
            "title": "高压柜前绝缘垫老化开裂",
            "location": "高压开关室",
            "level": "高风险",
            "owner": "李强",
            "deadline": "2026-03-16",
            "status": "整改中",
            "measure": "更换绝缘垫并完成现场复查",
            "source": "专项检查",
        },
        {
            "ticket_no": "YH-202603-011",
            "title": "临时用电箱未设置漏电保护测试记录",
            "location": "检修作业区 B",
            "level": "高风险",
            "owner": "赵倩",
            "deadline": "2026-03-15",
            "status": "已逾期",
            "measure": "补测并上传记录，锁定责任班组",
            "source": "现场抽查",
        },
        {
            "ticket_no": "YH-202603-022",
            "title": "电缆沟可燃杂物未及时清理",
            "location": "厂房东侧电缆沟",
            "level": "低风险",
            "owner": "陈超",
            "deadline": "2026-03-20",
            "status": "待复查",
            "measure": "清理杂物并完成照片留档",
            "source": "班组上报",
        },
    ]
    return render_template("safety_hazards.html", summary=summary, hazards=hazards)


@bp.route("/safety/cases")
@login_required
def cases():
    featured_case = {
        "title": "低压配电柜检修触电事故复盘",
        "type": "触电伤害",
        "scene": "检修停电确认不足",
        "loss": "1 人轻伤，设备停运 2 小时",
        "cause": [
            "未执行验电流程",
            "工作票与现场措施不一致",
            "班前安全交底流于形式",
        ],
        "advice": [
            "设置倒闸操作双人复核",
            "检修前强制上传验电照片",
            "按案例要点生成班组培训题",
        ],
    }
    case_cards = [
        {
            "title": "电缆沟积水导致短路跳闸",
            "tag": "设备故障",
            "severity": "较大",
            "date": "2025-11-12",
            "keywords": ["电缆沟", "短路", "排水"],
        },
        {
            "title": "临时用电箱漏保失效引发人身风险",
            "tag": "现场违章",
            "severity": "重大隐患",
            "date": "2026-01-08",
            "keywords": ["漏保", "临时用电", "巡检"],
        },
        {
            "title": "高处更换绝缘子坠落险情",
            "tag": "高处作业",
            "severity": "一般",
            "date": "2025-10-21",
            "keywords": ["高处作业", "监护", "工器具"],
        },
    ]
    return render_template(
        "safety_cases.html",
        featured_case=featured_case,
        case_cards=case_cards,
    )


@bp.route("/safety/training")
@login_required
def training():
    exam_stats = {
        "question_bank": 386,
        "active_exams": 6,
        "pass_rate": "92%",
        "wrong_questions": 48,
    }
    papers = [
        {
            "name": "电气安全入厂考试",
            "mode": "固定试卷",
            "duration": "30 分钟",
            "audience": "新员工",
            "status": "进行中",
            "publish_at": "2026-03-12 09:00",
            "manager": "培训管理员",
            "participants": 48,
        },
        {
            "name": "倒闸操作专项测评",
            "mode": "随机组卷",
            "duration": "20 分钟",
            "audience": "运行班组",
            "status": "待发布",
            "publish_at": "2026-03-18 14:00",
            "manager": "运行培训专员",
            "participants": 32,
        },
        {
            "name": "事故案例月度复训",
            "mode": "案例闯关",
            "duration": "15 分钟",
            "audience": "全员",
            "status": "已完成",
            "publish_at": "2026-03-05 10:00",
            "manager": "安全培训负责人",
            "participants": 126,
        },
    ]
    return render_template(
        "safety_training.html",
        exam_stats=exam_stats,
        papers=papers,
    )


@bp.route("/safety/dashboard")
@login_required
def dashboard():
    kpis = [
        {"label": "本月问答次数", "value": "12,846", "trend": "+18.2%"},
        {"label": "隐患闭环率", "value": "86%", "trend": "+6.4%"},
        {"label": "培训覆盖率", "value": "93%", "trend": "+4.1%"},
        {"label": "标准引用命中率", "value": "78%", "trend": "+9.7%"},
    ]
    hot_topics = [
        ("工作票签发流程", 132),
        ("配电柜巡检标准", 118),
        ("漏电保护测试周期", 97),
        ("电缆火灾处置", 81),
    ]
    dept_scores = [
        {"name": "运行部", "score": 95, "risk": "低"},
        {"name": "检修部", "score": 88, "risk": "中"},
        {"name": "动力车间", "score": 82, "risk": "中"},
        {"name": "外协班组", "score": 71, "risk": "高"},
    ]
    monthly = [58, 64, 71, 69, 83, 96, 102]
    return render_template(
        "safety_dashboard.html",
        kpis=kpis,
        hot_topics=hot_topics,
        dept_scores=dept_scores,
        monthly=monthly,
    )
