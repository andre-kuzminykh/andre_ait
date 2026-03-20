"""
ReportService — генерация HTML-отчётов и их хранение.

## Трассируемость
Feature: F001 — AI Maturity Assessment
Scenarios: SC005

## Бизнес-контекст
Генерирует стилизованный HTML-отчёт с брендингом Andre AI Technologies,
сохраняет на диск, отдаёт по ID.

## Зависимости
- core.config
"""

import html as html_mod
import os
import uuid

from core.config import config

REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "reports")


class ReportService:
    def __init__(self):
        os.makedirs(REPORTS_DIR, exist_ok=True)

    def save_report(self, html: str) -> str:
        os.makedirs(REPORTS_DIR, exist_ok=True)
        report_id = uuid.uuid4().hex[:12]
        path = os.path.join(REPORTS_DIR, f"{report_id}.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        return report_id

    def get_report_url(self, report_id: str) -> str:
        base = config.REPORT_BASE_URL.rstrip("/")
        return f"{base}/api/v1/reports/{report_id}"

    def get_report_path(self, report_id: str) -> str | None:
        if not all(c in "0123456789abcdef" for c in report_id):
            return None
        path = os.path.join(REPORTS_DIR, f"{report_id}.html")
        if not os.path.isfile(path):
            return None
        return path

    def read_report(self, report_id: str) -> str | None:
        path = self.get_report_path(report_id)
        if not path:
            return None
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    def generate_html_report(self, result: dict, analysis: str | None) -> str:
        categories_html = self._build_categories_html(result["categories"])
        strengths_html = ", ".join(
            f'{s["emoji"]} {html_mod.escape(s["name"])} ({s["percent"]}%)'
            for s in result["strengths"]
        )
        weaknesses_html = ", ".join(
            f'{w["emoji"]} {html_mod.escape(w["name"])} ({w["percent"]}%)'
            for w in result["weaknesses"]
        )
        analysis_html = ""
        if analysis:
            analysis_html = self._text_to_html(analysis)

        return HTML_TEMPLATE.format(
            total_percent=result["total_percent"],
            maturity_level=html_mod.escape(result["maturity_level"]),
            reliability=html_mod.escape(result["reliability"]),
            categories_html=categories_html,
            strengths=strengths_html,
            weaknesses=weaknesses_html,
            analysis_section=analysis_html,
        )

    @staticmethod
    def _build_categories_html(categories: list[dict]) -> str:
        rows = []
        for c in categories:
            tentative = (
                ' <span class="text-[var(--text-muted)] text-xs">≈</span>'
                if c.get("tentative") else ""
            )
            name = html_mod.escape(c["name"])
            pct = c["percent"]
            bar_width = max(pct, 1)
            rows.append(
                f'<div class="w-full">\n'
                f'  <div class="flex justify-between items-end mb-2">\n'
                f'    <span class="text-sm md:text-base font-bold text-[var(--text-main)]">'
                f'{c["emoji"]} {name}{tentative}</span>\n'
                f'    <span class="text-sm md:text-base font-mono font-bold '
                f'text-[var(--text-main)]">{pct}%</span>\n'
                f'  </div>\n'
                f'  <div class="w-full h-3 md:h-4 bg-black/10 dark:bg-white/10 '
                f'rounded-full overflow-hidden shadow-inner">\n'
                f'    <div class="h-full bg-gradient-to-r from-brand-purple to-brand-orange '
                f'rounded-full transition-all duration-1000 ease-out" '
                f'style="width: {bar_width}%"></div>\n'
                f'  </div>\n'
                f'</div>'
            )
        return "\n".join(rows)

    @staticmethod
    def _text_to_html(text: str) -> str:
        _SECTION_EMOJIS = frozenset("📊🔍🤖📋💡🗺📌📐⚠️")
        _SUB_HEADER_EMOJIS = frozenset("🚀📅🎯")

        lines = text.split("\n")
        result_lines = []
        for line in lines:
            stripped = line.strip()
            if not stripped:
                result_lines.append("")
                continue
            first_char = stripped[0]
            if first_char in _SECTION_EMOJIS:
                result_lines.append(
                    f'<h3 class="text-lg md:text-xl font-bold text-[var(--text-main)] '
                    f'mt-8 mb-3 pt-4 border-t border-[var(--glass-border)]">'
                    f'{html_mod.escape(stripped)}</h3>'
                )
            elif first_char in _SUB_HEADER_EMOJIS:
                colon_idx = stripped.find(":")
                if colon_idx != -1:
                    label = html_mod.escape(stripped[:colon_idx + 1])
                    body = html_mod.escape(stripped[colon_idx + 1:])
                    result_lines.append(
                        f'<h3 class="text-lg md:text-xl text-[var(--text-main)] '
                        f'mt-8 mb-3 pt-4 border-t border-[var(--glass-border)]">'
                        f'<span class="font-bold">{label}</span>{body}</h3>'
                    )
                else:
                    result_lines.append(
                        f'<h3 class="text-lg md:text-xl font-bold text-[var(--text-main)] '
                        f'mt-8 mb-3 pt-4 border-t border-[var(--glass-border)]">'
                        f'{html_mod.escape(stripped)}</h3>'
                    )
            elif stripped.startswith("•") or stripped.startswith("-"):
                result_lines.append(
                    f'<li class="text-sm md:text-base text-[var(--text-main)] ml-5 mb-1">'
                    f'{html_mod.escape(stripped.lstrip("•- "))}</li>'
                )
            elif stripped.startswith("[") and "→" in stripped:
                result_lines.append(
                    f'<div class="process-chain bg-brand-purple/5 dark:bg-brand-purple/10 '
                    f'border border-brand-purple/20 rounded-lg p-4 my-3 font-mono text-xs '
                    f'md:text-sm whitespace-pre-wrap break-words">'
                    f'{html_mod.escape(stripped)}</div>'
                )
            else:
                result_lines.append(
                    f'<p class="text-sm md:text-base text-[var(--text-main)] mb-2">'
                    f'{html_mod.escape(stripped)}</p>'
                )
        return "\n".join(result_lines)


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="ru" class="dark">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>Andre AI - Диагностика ИИ-зрелости</title>
<meta name="description" content="Отчёт: Диагностика ИИ-зрелости. Результаты по категориям, уровень зрелости и надёжность.">
<meta property="og:type" content="website">
<meta property="og:title" content="Отчёт: Диагностика ИИ-зрелости | Andre AI">
<meta property="og:description" content="Отчёт: Диагностика ИИ-зрелости. Результаты по категориям, уровень зрелости и надёжность.">
<meta property="og:image" content="https://images.unsplash.com/photo-1620712943543-bcc4688e7485?q=80&w=1200&auto=format&fit=crop">
<meta property="twitter:card" content="summary_large_image">
<meta property="twitter:title" content="Отчёт: Диагностика ИИ-зрелости | Andre AI">
<meta property="twitter:description" content="Отчёт: Диагностика ИИ-зрелости. Результаты по категориям, уровень зрелости и надёжность.">
<meta property="twitter:image" content="https://images.unsplash.com/photo-1620712943543-bcc4688e7485?q=80&w=1200&auto=format&fit=crop">
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<script src="https://cdn.tailwindcss.com"></script>
<script>
tailwind.config = {{
  darkMode: 'class',
  theme: {{
    extend: {{
      fontFamily: {{ mono: ['"JetBrains Mono"', 'monospace'] }},
      colors: {{ brand: {{ purple: '#8854F3', orange: '#F97316' }} }}
    }}
  }}
}}
</script>
<style>
:root {{
  --brand-purple: #8854F3;
  --brand-orange: #F97316;
  --bg-main: #f8fafc;
  --text-main: #0f172a;
  --text-muted: #64748b;
  --glass-bg: rgba(255, 255, 255, 0.4);
  --glass-border: rgba(0, 0, 0, 0.08);
  --grid-color-purple: rgba(136, 84, 243, 0.08);
  --grid-color-orange: rgba(249, 115, 22, 0.08);
  --card-bg: rgba(0, 0, 0, 0.03);
  --header-bg: rgba(255, 255, 255, 0.95);
}}
.dark {{
  --bg-main: #050505;
  --text-main: #E5E7EB;
  --text-muted: #9ca3af;
  --glass-bg: rgba(255, 255, 255, 0.03);
  --glass-border: rgba(255, 255, 255, 0.05);
  --grid-color-purple: rgba(136, 84, 243, 0.04);
  --grid-color-orange: rgba(249, 115, 22, 0.04);
  --card-bg: rgba(255, 255, 255, 0.03);
  --header-bg: rgba(5, 5, 5, 0.95);
}}
body {{
  font-family: 'JetBrains Mono', monospace;
  background-color: var(--bg-main);
  color: var(--text-main);
  margin: 0;
  width: 100vw;
  min-height: 100vh;
  transition: background-color 0.5s ease, color 0.5s ease;
  overflow-x: hidden;
}}
::selection {{ background: var(--brand-purple); color: #FFFFFF; }}
.bg-grid {{
  background-size: 40px 40px;
  background-image:
    linear-gradient(to right, var(--grid-color-purple) 1px, transparent 1px),
    linear-gradient(to bottom, var(--grid-color-orange) 1px, transparent 1px);
  transition: background-image 0.5s ease;
}}
.blob {{
  position: fixed; z-index: -10; opacity: 0.5;
  transform: scale(1) translateZ(0);
  will-change: transform, opacity;
  background-size: contain; background-repeat: no-repeat; background-position: center;
  mix-blend-mode: multiply;
}}
.dark .blob {{ mix-blend-mode: screen; }}
.blob-purple {{ background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' width='1600' height='1600' viewBox='0 0 500 500'%3e%3cdefs%3e%3cradialGradient id='grad' cx='50%25' cy='50%25' r='50%25'%3e%3cstop offset='0%25' stop-color='%238854F3' stop-opacity='1'/%3e%3cstop offset='100%25' stop-color='%238854F3' stop-opacity='0'/%3e%3c/radialGradient%3e%3c/defs%3e%3ccircle cx='250' cy='250' r='250' fill='url(%23grad)'/%3e%3c/svg%3e"); }}
.blob-orange {{ background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' width='1600' height='1600' viewBox='0 0 500 500'%3e%3cdefs%3e%3cradialGradient id='grad' cx='50%25' cy='50%25' r='50%25'%3e%3cstop offset='0%25' stop-color='%23F97316' stop-opacity='1'/%3e%3cstop offset='100%25' stop-color='%23F97316' stop-opacity='0'/%3e%3c/radialGradient%3e%3c/defs%3e%3ccircle cx='250' cy='250' r='250' fill='url(%23grad)'/%3e%3c/svg%3e"); }}
.grain-overlay {{
  position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
  pointer-events: none; z-index: 20; opacity: 0.03;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='noiseFilter'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23noiseFilter)'/%3E%3C/svg%3E");
  mix-blend-mode: overlay;
}}
.glass-panel {{
  background: var(--glass-bg);
  backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
  border: 1px solid var(--glass-border);
  border-radius: 1.25rem;
  box-shadow: 0 4px 30px rgba(0, 0, 0, 0.05);
}}
.data-card {{
  background: var(--card-bg);
  border: 1px solid var(--glass-border);
  border-radius: 1rem;
  transition: all 0.3s ease;
}}
.data-card:hover {{
  border-color: rgba(136, 84, 243, 0.3);
  background: rgba(136, 84, 243, 0.02);
}}
.text-gradient {{
  background: linear-gradient(to right, var(--brand-purple), var(--brand-orange));
  -webkit-background-clip: text; -webkit-text-fill-color: transparent;
  background-clip: text;
}}
.logo-container {{ display: flex; align-items: center; }}
header {{
  background-color: var(--header-bg);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}}
@media print {{
  body {{ background: #fff !important; color: #000 !important; }}
  .blob, .grain-overlay, .bg-grid, #theme-toggle, .no-print {{ display: none !important; }}
  .glass-panel, .data-card {{ background: #fff !important; border-color: #ddd !important; backdrop-filter: none !important; }}
  header {{ position: relative !important; background: #fff !important; backdrop-filter: none !important; }}
  main {{ padding-top: 1rem !important; }}
  .text-gradient {{ -webkit-text-fill-color: #8854F3; }}
  * {{ -webkit-print-color-adjust: exact !important; print-color-adjust: exact !important; }}
}}
</style>
</head>
<body class="antialiased">
<div class="fixed inset-0 overflow-hidden pointer-events-none z-0">
  <div class="absolute inset-0 bg-grid z-10"></div>
  <div id="blob1" class="blob blob-purple w-[30rem] h-[30rem] md:w-[40rem] md:h-[40rem] lg:w-[50rem] lg:h-[50rem]"></div>
  <div id="blob2" class="blob blob-orange w-[30rem] h-[30rem] md:w-[40rem] md:h-[40rem] lg:w-[50rem] lg:h-[50rem]"></div>
  <div class="grain-overlay"></div>
</div>
<header class="fixed top-0 left-0 w-full py-2 px-4 md:py-2 md:px-6 z-40 flex justify-between items-center border-b border-[var(--glass-border)] shadow-sm dark:shadow-none transition-colors duration-500">
  <div class="logo-container gap-2 md:gap-3 shrink-0 min-w-0">
    <img src="https://i.ibb.co/gn7SmgY/866f2500-dd81-4d09-8c0f-2b55c25a3464-removalai-preview.png" alt="AIT Logo" class="h-10 md:h-12 w-auto object-contain shrink-0 scale-[1.1] origin-left"/>
    <div class="flex flex-col justify-center text-left">
      <span class="font-mono text-[10px] md:text-[13px] font-bold text-[var(--text-main)] leading-[1.15] whitespace-nowrap transition-colors duration-500">Andre AI</span>
      <span class="font-mono text-[10px] md:text-[13px] font-bold text-[var(--text-main)] leading-[1.15] whitespace-nowrap transition-colors duration-500">Technologies</span>
    </div>
  </div>
  <div class="flex items-center gap-3">
    <button id="theme-toggle" class="w-8 h-8 md:w-9 md:h-9 flex items-center justify-center text-[var(--text-main)] hover:scale-110 transition-transform shrink-0 z-50 bg-transparent border-none cursor-pointer">
      <i class="fa-solid fa-moon dark:hidden text-lg"></i>
      <i class="fa-solid fa-sun hidden dark:block text-lg"></i>
    </button>
  </div>
</header>
<main class="relative z-30 w-full min-h-screen flex flex-col items-center pt-24 md:pt-32 pb-12 px-4 md:px-8">
  <div class="w-full max-w-4xl mb-8 flex flex-col text-center mt-2">
    <div class="inline-flex items-center space-x-3 px-4 py-1.5 rounded-full bg-black/5 dark:bg-white/10 backdrop-blur-md mb-4 uppercase tracking-widest text-[10px] md:text-xs font-bold text-[var(--text-main)] border border-[var(--glass-border)] w-max mx-auto">
      <span class="relative flex h-2 w-2">
        <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-brand-purple opacity-75"></span>
        <span class="relative inline-flex rounded-full h-2 w-2 bg-brand-purple"></span>
      </span>
      <span>Отчёт</span>
    </div>
    <h1 class="text-3xl md:text-5xl font-black uppercase tracking-tight mb-2">
      <span class="text-gradient">Диагностика ИИ-зрелости</span>
    </h1>
  </div>
  <div class="w-full max-w-4xl grid grid-cols-2 md:grid-cols-3 gap-4 mb-8">
    <div class="data-card p-6 flex flex-col items-center justify-center col-span-2 md:col-span-1 border-brand-orange/30">
      <span class="text-[var(--text-muted)] text-xs uppercase tracking-widest mb-2 text-center">Общий балл</span>
      <span class="text-4xl md:text-5xl font-black text-brand-orange">{total_percent}%</span>
    </div>
    <div class="data-card p-6 flex flex-col items-center justify-center border-brand-purple/30">
      <span class="text-[var(--text-muted)] text-xs uppercase tracking-widest mb-2 text-center">Уровень</span>
      <span class="text-lg md:text-xl font-bold text-[var(--text-main)] text-center">{maturity_level}</span>
    </div>
    <div class="data-card p-6 flex flex-col items-center justify-center">
      <span class="text-[var(--text-muted)] text-xs uppercase tracking-widest mb-2 text-center">Надёжность</span>
      <span class="text-lg md:text-xl font-bold text-[var(--text-main)] text-center">{reliability}</span>
    </div>
  </div>
  <div class="glass-panel w-full max-w-4xl p-6 md:p-10 mb-8">
    <h2 class="text-xl md:text-2xl font-bold w-full text-left mb-8 uppercase tracking-wider text-[var(--text-main)] border-b border-[var(--glass-border)] pb-4">Результаты по категориям</h2>
    <div class="flex flex-col gap-6">
      {categories_html}
    </div>
  </div>
  <div class="w-full max-w-4xl grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
    <div class="glass-panel p-6">
      <h2 class="text-base md:text-lg font-bold text-[var(--text-main)] mb-3 uppercase tracking-wider">💪 Сильные стороны</h2>
      <p class="text-sm md:text-base text-[var(--text-main)]">{strengths}</p>
    </div>
    <div class="glass-panel p-6">
      <h2 class="text-base md:text-lg font-bold text-[var(--text-main)] mb-3 uppercase tracking-wider">📈 Зоны роста</h2>
      <p class="text-sm md:text-base text-[var(--text-main)]">{weaknesses}</p>
    </div>
  </div>
  <div class="glass-panel w-full max-w-4xl p-6 md:p-10 mb-8">
    <h2 class="text-xl md:text-2xl font-bold w-full text-left mb-6 uppercase tracking-wider text-[var(--text-main)] border-b border-[var(--glass-border)] pb-4">Расширенный анализ</h2>
    {analysis_section}
  </div>
  <div class="w-full max-w-4xl mt-2 text-center">
    <p class="text-[10px] md:text-xs text-[var(--text-muted)] uppercase tracking-widest bg-black/5 dark:bg-white/5 inline-block px-4 py-2 rounded-lg border border-[var(--glass-border)]">
      <i class="fa-solid fa-robot mr-1"></i> Сгенерировано ботом «Диагностика ИИ-зрелости»
    </p>
  </div>
</main>
<script>
const themeToggle = document.getElementById('theme-toggle');
if (themeToggle) {{
  themeToggle.addEventListener('click', () => {{
    document.documentElement.classList.toggle('dark');
  }});
}}
const blob1 = document.getElementById('blob1');
const blob2 = document.getElementById('blob2');
let wanderTime = 0;
let blob1State = {{ x: window.innerWidth * 0.45, y: window.innerHeight * 0.4 }};
let blob2State = {{ x: window.innerWidth * 0.55, y: window.innerHeight * 0.6 }};
function animateBlobs() {{
  wanderTime += 0.002;
  const cx = window.innerWidth / 2;
  const cy = window.innerHeight / 2;
  const baseOffset = Math.min(window.innerWidth * 0.18, 180);
  const radiusX = Math.min(window.innerWidth * 0.1, 100);
  const radiusY = Math.min(window.innerHeight * 0.1, 100);
  let targetX1 = (cx - baseOffset) + radiusX * Math.cos(wanderTime) - (blob1.offsetWidth||800)/2;
  let targetY1 = cy + radiusY * Math.sin(wanderTime * 1.2) - (blob1.offsetHeight||800)/2;
  let targetX2 = (cx + baseOffset) + radiusX * Math.cos(wanderTime + Math.PI) - (blob2.offsetWidth||800)/2;
  let targetY2 = cy + radiusY * Math.sin((wanderTime + Math.PI) * 1.2) - (blob2.offsetHeight||800)/2;
  blob1State.x += (targetX1 - blob1State.x) * 0.03;
  blob1State.y += (targetY1 - blob1State.y) * 0.03;
  blob2State.x += (targetX2 - blob2State.x) * 0.03;
  blob2State.y += (targetY2 - blob2State.y) * 0.03;
  blob1.style.transform = `translate3d(${{blob1State.x}}px, ${{blob1State.y}}px, 0)`;
  blob2.style.transform = `translate3d(${{blob2State.x}}px, ${{blob2State.y}}px, 0)`;
  requestAnimationFrame(animateBlobs);
}}
animateBlobs();
</script>
</body>
</html>"""
