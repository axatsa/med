PREDICTOR_LABELS = {
    "sflt1_pigf_ratio": {
        "ru": "Высокое соотношение sFlt-1/PlGF",
        "uz": "Yuqori sFlt-1/PlGF nisbati",
    },
    "il6": {
        "ru": "Высокий уровень IL-6",
        "uz": "Yuqori IL-6 darajasi",
    },
    "vegfa": {
        "ru": "Низкий уровень VEGF-А",
        "uz": "Past VEGF-A darajasi",
    },
    "il6_genetics": {
        "ru": "IL6 rs1800795 – GG генотип",
        "uz": "IL6 rs1800795 – GG genotip",
    },
    "pn_degree": {
        "ru": "Плацентарная недостаточность",
        "uz": "Yo'ldosh yetishmovchiligi",
    },
    "map": {
        "ru": "Повышенное MAP",
        "uz": "Yuqori MAP",
    },
    "il10_genetics": {
        "ru": "IL10 rs1800896 – AA генотип",
        "uz": "IL10 rs1800896 – AA genotip",
    },
    "il10": {
        "ru": "Сниженный уровень IL-10",
        "uz": "Past IL-10 darajasi",
    },
    "mcp1": {
        "ru": "Высокий уровень MCP-1",
        "uz": "Yuqori MCP-1 darajasi",
    },
    "previous_pe": {
        "ru": "ПЭ в анамнезе",
        "uz": "Anamnezda PE",
    },
    "pi_uterine": {
        "ru": "Высокий индекс пульсации маточных артерий",
        "uz": "Bachadon arteriyasi pulsatsiya indeksi yuqori",
    },
    "fgr": {
        "ru": "Задержка роста плода",
        "uz": "Homila o'sishining kechikishi",
    },
    "hypertension": {
        "ru": "Хроническая гипертензия",
        "uz": "Surunkali gipertenziya",
    },
    "ip10": {
        "ru": "Высокий уровень IP-10",
        "uz": "Yuqori IP-10 darajasi",
    },
    "tnf_alpha": {
        "ru": "Высокий уровень TNF-α",
        "uz": "Yuqori TNF-α darajasi",
    },
    "gestational_age": {
        "ru": "Ранний срок беременности",
        "uz": "Homiladorlikning erta muddati",
    },
}

RECOMMENDATIONS = {
    "HIGH": {
        "ru": [
            "Усиленный контроль АД и клинического состояния",
            "Допплерометрия каждые 1–2 недели",
            "Профилактика низкими дозами аспирина (если не противопоказано)",
            "Повторное исследование ангиогенных и иммунных маркеров",
            "Оценка признаков прогрессирования преэклампсии",
            "Рассмотреть госпитализацию при ухудшении состояния",
        ],
        "uz": [
            "Qon bosimi va klinik holatni kuchaytirish nazorati",
            "Har 1-2 haftada dopplerometriya",
            "Kam dozali aspirin bilan profilaktika (agar kontrendikatsiya yo'q bo'lsa)",
            "Angiogen va immunologik markerlarni qayta tekshirish",
            "Preeklampsiya progressiyasi belgilarini baholash",
            "Ahvol yomonlashganda kasalxonaga yotqizishni ko'rib chiqish",
        ],
    },
    "MODERATE": {
        "ru": [
            "Контроль АД 2 раза в неделю",
            "Допплерометрия каждые 2–3 недели",
            "Мониторинг лабораторных показателей ежемесячно",
            "Ограничение физической нагрузки",
            "При нарастании симптомов — повторная оценка риска",
        ],
        "uz": [
            "Haftada 2 marta qon bosimini nazorat qilish",
            "Har 2-3 haftada dopplerometriya",
            "Har oyda laboratoriya ko'rsatkichlarini monitoring qilish",
            "Jismoniy faollikni cheklash",
            "Alomatlar kuchaysa — xavfni qayta baholash",
        ],
    },
    "LOW": {
        "ru": [
            "Стандартный мониторинг беременности",
            "Плановая допплерометрия",
            "Повторная оценка при появлении симптомов",
        ],
        "uz": [
            "Homiladorlikning standart monitoringi",
            "Rejalashtirilgan dopplerometriya",
            "Alomatlar paydo bo'lganda qayta baholash",
        ],
    },
}

RISK_LABELS = {
    "HIGH": {"ru": "ВЫСОКИЙ РИСК", "uz": "YUQORI XAVF"},
    "MODERATE": {"ru": "УМЕРЕННЫЙ РИСК", "uz": "O'RTACHA XAVF"},
    "LOW": {"ru": "НИЗКИЙ РИСК", "uz": "PAST XAVF"},
}

RISK_ALERT = {
    "HIGH": {
        "ru": "Высокая вероятность перехода плацентарной недостаточности в преэклампсию. Рекомендуется усиленное наблюдение и ранняя профилактика.",
        "uz": "Yo'ldosh yetishmovchiligining preeklampsiyaga o'tish ehtimoli yuqori. Kuchaytirish nazorati va erta profilaktika tavsiya etiladi.",
    },
    "MODERATE": {
        "ru": "Умеренный риск перехода. Требуется регулярный мониторинг и коррекция факторов риска.",
        "uz": "O'rtacha o'tish xavfi. Muntazam monitoring va xavf omillarini tuzatish kerak.",
    },
    "LOW": {
        "ru": "Низкий риск перехода. Продолжайте стандартное наблюдение.",
        "uz": "Past o'tish xavfi. Standart kuzatuvni davom ettiring.",
    },
}

REPORT_TITLES = {
    "ru": {
        "main": "ИММУНОГЕНЕТИЧЕСКИЙ ПРОГНОЗ РИСКА ПЕРЕХОДА",
        "sub": "ПЛАЦЕНТАРНОЙ НЕДОСТАТОЧНОСТИ → ПРЕЭКЛАМПСИЯ",
        "section_patient": "1. ДАННЫЕ ПАЦИЕНТКИ",
        "section_placental": "2. ПЛАЦЕНТАРНАЯ НЕДОСТАТОЧНОСТЬ",
        "section_immuno": "3. ИММУНОЛОГИЧЕСКИЕ МАРКЕРЫ (pg/ml)",
        "section_angio": "4. АНГИОГЕННЫЕ ФАКТОРЫ (pg/ml)",
        "section_genetic": "5. ГЕНЕТИЧЕСКИЕ ПОЛИМОРФИЗМЫ",
        "section_result": "6. РЕЗУЛЬТАТ ПРОГНОЗА",
        "section_predictors": "7. ОСНОВНЫЕ ПРЕДИКТОРЫ",
        "section_recs": "8. РЕКОМЕНДАЦИИ",
        "section_model": "9. ИНФОРМАЦИЯ О МОДЕЛИ",
        "risk_title": "РИСК ПЕРЕХОДА ПН В ПРЕЭКЛАМПСИЮ",
        "probability": "Вероятность прогрессирования ПН → ПЭ",
        "low": "НИЗКИЙ (<30%)",
        "moderate": "УМЕРЕННЫЙ (30–60%)",
        "high": "ВЫСОКИЙ (>60%)",
        "contribution": "Вклад",
        "algorithm": "Алгоритм:",
        "auc": "Внутренняя валидация (AUC):",
        "updated": "Дата последнего обновления модели:",
        "disclaimer": "Данный инструмент предназначен для поддержки клинических решений и не заменяет мнение врача.",
    },
    "uz": {
        "main": "IMMUNOGENETIK XAVF PROGNOZI",
        "sub": "YO'LDOSH YETISHMOVCHILIGI → PREEKLAMPSIYA",
        "section_patient": "1. BEMORNING MA'LUMOTLARI",
        "section_placental": "2. YO'LDOSH YETISHMOVCHILIGI",
        "section_immuno": "3. IMMUNOLOGIK MARKERLAR (pg/ml)",
        "section_angio": "4. ANGIOGEN OMILLAR (pg/ml)",
        "section_genetic": "5. GENETIK POLIMORFIZMLAR",
        "section_result": "6. PROGNOZ NATIJASI",
        "section_predictors": "7. ASOSIY PREDIKTORLAR",
        "section_recs": "8. TAVSIYALAR",
        "section_model": "9. MODEL HAQIDA MA'LUMOT",
        "risk_title": "YN dan PE ga O'TISH XAVFI",
        "probability": "YN → PE progressiyasi ehtimoli",
        "low": "PAST (<30%)",
        "moderate": "O'RTACHA (30-60%)",
        "high": "YUQORI (>60%)",
        "contribution": "Hissa",
        "algorithm": "Algoritm:",
        "auc": "Ichki validatsiya (AUC):",
        "updated": "Model oxirgi yangilanish sanasi:",
        "disclaimer": "Bu vosita klinik qarorlarni qo'llab-quvvatlash uchun mo'ljallangan va shifokor fikrini almashtirmaydi.",
    },
}
