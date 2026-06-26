import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta, timezone
import math
import os
from dotenv import load_dotenv

load_dotenv()

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="US Stock Investment Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Design tokens ─────────────────────────────────────────────────────────────
# 배경: 눈이 편한 짙은 인디고-슬레이트 계열
# 텍스트: 채도 있는 라벤더-화이트 / 서브텍스트: 하늘색 계열 (흰색보다 눈에 잘 띔)
C = {
    "bg":          "#0d1021",   # 짙은 남색-검정
    "surface":     "#161929",   # 카드 배경
    "surface_low": "#11141f",   # 사이드바 배경
    "surface_hi":  "#1e2238",   # 호버 배경
    "surface_hst": "#252a42",   # 차트 그리드선
    "border":      "#3a4060",   # 경계선
    "text":        "#e8ecff",   # 주 텍스트: 라벤더-화이트 (눈부심 없이 선명)
    "text_muted":  "#a8b8e8",   # 보조 텍스트: 밝은 파랑-라벤더 (충분한 대비)
    "primary":     "#7eb8ff",   # 포인트: 소프트 파랑
    "green":       "#6ee7a0",   # 상승: 소프트 그린
    "red":         "#ff8f8f",   # 하락: 소프트 레드
    "outline":     "#8898cc",   # 보조 강조
}

def hex_to_rgba(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── 전역 배경 (메인 + 앱 전체) ── */
html, body, [class*="css"] {{
    font-family: 'Inter', sans-serif;
    background-color: {C['bg']};
    color: {C['text']};
}}
/* Streamlit 메인 영역 배경 강제 override */
.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"],
section.main,
.main {{
    background-color: {C['bg']} !important;
}}
/* 메인 컨텐츠 블록 */
.block-container {{
    background-color: {C['bg']} !important;
    padding-top: 1.5rem;
    padding-bottom: 2rem;
}}
/* 혹시 남은 흰 배경 컴포넌트들 */
[data-testid="stVerticalBlock"],
[data-testid="stHorizontalBlock"] {{
    background-color: transparent !important;
}}
#MainMenu, footer, header {{ visibility: hidden; }}

/* ── 메인 영역 모든 텍스트 ── */
.stMarkdown, .stMarkdown p, .stMarkdown li,
div[data-testid="stText"], span {{
    color: {C['text']};
}}

/* ── Streamlit 기본 위젯 텍스트 강제 override ── */
label, .stSelectbox label, .stTextInput label,
.stNumberInput label, .stSlider label,
.stDateInput label, .stCheckbox label,
.stRadio label, p, small, .stCaption p {{
    color: {C['text_muted']} !important;
    font-size: 13px !important;
}}
/* 선택된 값 / 입력값 */
.stSelectbox [data-baseweb="select"] span,
.stTextInput input, .stNumberInput input,
input[type="text"], input[type="number"] {{
    color: {C['text']} !important;
    background-color: {C['surface_hi']} !important;
    border-color: {C['border']} !important;
}}
/* 슬라이더 값 표시 */
.stSlider [data-testid="stTickBarMin"],
.stSlider [data-testid="stTickBarMax"],
.stSlider span {{
    color: {C['text_muted']} !important;
}}

/* ── 사이드바 ── */
[data-testid="stSidebar"] {{
    background-color: {C['surface_low']};
    border-right: 2px solid {C['primary']};   /* 메인과 구분되는 파란 테두리 */
}}
[data-testid="stSidebar"] * {{
    color: {C['text_muted']};
}}
[data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2 {{
    color: {C['text']} !important;
    font-size: 18px !important;
}}
[data-testid="stSidebar"] h3, [data-testid="stSidebar"] .stMarkdown h3 {{
    color: {C['primary']} !important;
    font-size: 11px !important;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    font-weight: 700;
}}
[data-testid="stSidebar"] label {{
    color: {C['text']} !important;
    font-size: 13px !important;
    font-weight: 500 !important;
}}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] small,
[data-testid="stSidebar"] .stCaption p {{
    color: {C['text_muted']} !important;
    font-size: 12px !important;
}}
[data-testid="stSidebar"] .stButton button {{
    background: {C['surface_hi']};
    color: {C['text']} !important;
    border: 1px solid {C['border']};
}}
[data-testid="stSidebar"] .stTextInput input,
[data-testid="stSidebar"] .stNumberInput input {{
    color: {C['text']} !important;
    background: {C['surface_hi']} !important;
    border-color: {C['border']} !important;
}}
/* expander 제목 */
[data-testid="stSidebar"] .stExpander summary span,
.stExpander summary span {{
    color: {C['text']} !important;
    font-size: 13px !important;
    font-weight: 600 !important;
}}
/* selectbox 드롭다운 */
[data-testid="stSidebar"] [data-baseweb="select"] span {{
    color: {C['text']} !important;
}}

/* ── 커스텀 컴포넌트 ── */
.kpi-card {{
    background: {C['surface']};
    border: 1px solid {C['border']};
    border-radius: 8px;
    padding: 14px 16px;
    font-family: 'JetBrains Mono', monospace;
}}
.kpi-ticker {{ font-size: 11px; font-weight: 700; color: {C['primary']};
               letter-spacing: 0.1em; text-transform: uppercase; }}
.kpi-price  {{ font-size: 22px; font-weight: 700; color: {C['text']}; margin: 4px 0 2px; }}
.kpi-pos    {{ color: {C['green']}; font-size: 13px; font-weight: 700; }}
.kpi-neg    {{ color: {C['red']};   font-size: 13px; font-weight: 700; }}
.kpi-sub    {{ color: {C['text_muted']}; font-size: 11px; margin-top: 4px; }}

.section-header {{ font-size: 17px; font-weight: 700; color: {C['text']}; margin-bottom: 4px; }}
.section-sub    {{ font-size: 13px; color: {C['text_muted']}; margin-bottom: 16px; }}

.ticker-tape {{ background: {C['surface_low']}; border-top: 1px solid {C['border']};
                border-bottom: 1px solid {C['border']}; padding: 8px 0;
                overflow: hidden; white-space: nowrap; margin-bottom: 24px; }}
.ticker-inner {{ display: inline-block; animation: marquee 40s linear infinite;
                 font-family: 'JetBrains Mono', monospace; font-size: 12px; }}
@keyframes marquee {{ 0% {{ transform: translateX(0); }} 100% {{ transform: translateX(-50%); }} }}
.t-pos {{ color: {C['green']}; font-weight: 600; }}
.t-neg {{ color: {C['red']};   font-weight: 600; }}
.t-sym {{ color: {C['text']}; margin-right: 4px; font-weight: 700; }}
.t-sep {{ color: {C['border']}; margin: 0 24px; }}

.divider {{ border-top: 1px solid {C['border']}; margin: 24px 0; }}

.stat-box {{
    background: {C['surface']}; border: 1px solid {C['border']};
    border-radius: 8px; padding: 12px 16px; text-align: center;
    font-family: 'JetBrains Mono', monospace;
}}
.stat-label {{ font-size: 11px; color: {C['text_muted']}; text-transform: uppercase;
               letter-spacing: 0.08em; font-weight: 600; }}
.stat-val   {{ font-size: 20px; font-weight: 700; margin-top: 6px; color: {C['text']}; }}

.fg-container {{ background: {C['surface']}; border: 1px solid {C['border']};
                 border-radius: 8px; padding: 20px 24px; text-align: center; }}
.fg-label {{ font-size: 11px; color: {C['text_muted']}; letter-spacing: 0.1em;
             text-transform: uppercase; font-weight: 700; }}
.fg-value {{ font-family: 'JetBrains Mono', monospace; font-size: 48px; font-weight: 700; margin: 8px 0; }}
.fg-mood  {{ font-size: 14px; font-weight: 700; letter-spacing: 0.05em; text-transform: uppercase; }}

.data-badge {{
    display: inline-block; font-size: 11px; font-family: 'JetBrains Mono', monospace;
    padding: 3px 10px; border-radius: 4px; font-weight: 700; letter-spacing: 0.05em;
}}
.badge-live   {{ background: {hex_to_rgba(C['green'],  0.2)}; color: {C['green']}; }}
.badge-cached {{ background: {hex_to_rgba(C['primary'],0.2)}; color: {C['primary']}; }}
.badge-dummy  {{ background: {hex_to_rgba(C['outline'],0.2)}; color: {C['outline']}; }}

.market-status-open   {{ background: {hex_to_rgba(C['green'], 0.18)}; color: {C['green']};
                          border: 1px solid {hex_to_rgba(C['green'], 0.4)};
                          border-radius: 6px; padding: 8px 16px; font-family: 'JetBrains Mono', monospace;
                          font-size: 13px; font-weight: 700; display: inline-block; }}
.market-status-closed {{ background: {hex_to_rgba(C['red'], 0.15)}; color: {C['red']};
                          border: 1px solid {hex_to_rgba(C['red'], 0.4)};
                          border-radius: 6px; padding: 8px 16px; font-family: 'JetBrains Mono', monospace;
                          font-size: 13px; font-weight: 700; display: inline-block; }}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# COMPANY METADATA
# ══════════════════════════════════════════════════════════════════════════════

COMPANIES = {
    "NVDA":  {"name": "NVIDIA Corp",           "tier": 1, "base": 875,  "annual_ret": 1.45, "vol": 0.52},
    "AMD":   {"name": "Advanced Micro Devices", "tier": 1, "base": 164,  "annual_ret": 0.42, "vol": 0.48},
    "AVGO":  {"name": "Broadcom Inc",           "tier": 1, "base": 1320, "annual_ret": 0.88, "vol": 0.35},
    "TSM":   {"name": "Taiwan Semi",            "tier": 1, "base": 138,  "annual_ret": 0.65, "vol": 0.32},
    "MU":    {"name": "Micron Technology",      "tier": 1, "base": 132,  "annual_ret": 0.55, "vol": 0.44},
    "MRVL":  {"name": "Marvell Technology",     "tier": 1, "base": 78,   "annual_ret": 0.72, "vol": 0.50},
    "QCOM":  {"name": "Qualcomm",               "tier": 2, "base": 185,  "annual_ret": 0.18, "vol": 0.30},
    "ARM":   {"name": "Arm Holdings",           "tier": 2, "base": 124,  "annual_ret": 0.95, "vol": 0.58},
    "ASML":  {"name": "ASML Holding",           "tier": 2, "base": 720,  "annual_ret": 0.38, "vol": 0.28},
    "INTC":  {"name": "Intel Corp",             "tier": 2, "base": 34,   "annual_ret": -0.22, "vol": 0.38},
}

COLORS = [
    C["primary"], "#ffaba0", "#3ce42f", "#ffdad5",
    "#77ff62",    "#b7eaff", "#ffd2cc", "#4cd6ff", "#a4e6ff", "#859399",
]

def ticker_color(i: int) -> str:
    return COLORS[i % len(COLORS)]

PERIOD_MAP = {
    "1M": 21, "3M": 63, "6M": 126, "1Y": 252, "3Y": 756, "5Y": 1260,
    "YTD": None, "Custom": None,
}

# ══════════════════════════════════════════════════════════════════════════════
# MARKET STATUS
# ══════════════════════════════════════════════════════════════════════════════

def get_market_status():
    """Returns (now_et, is_open) for NYSE/NASDAQ. Uses pytz if available."""
    try:
        import pytz
        et = pytz.timezone("America/New_York")
        now = datetime.now(et)
    except Exception:
        # Fallback: EDT = UTC-4 (summer), EST = UTC-5 (winter)
        now = datetime.utcnow() - timedelta(hours=4)

    wd = now.weekday()  # 0=Mon … 6=Sun
    h, m = now.hour, now.minute
    after_open  = (h == 9 and m >= 30) or (h >= 10)
    before_close = h < 16
    is_open = (wd < 5) and after_open and before_close
    return now, is_open


# ══════════════════════════════════════════════════════════════════════════════
# DATA LAYER
# ══════════════════════════════════════════════════════════════════════════════

def _dummy_series(ticker: str, n_days: int = 1260) -> pd.DataFrame:
    info = COMPANIES.get(ticker, {"annual_ret": 0.3, "vol": 0.4, "base": 100})
    np.random.seed(abs(hash(ticker)) % (2**31))
    mu    = info["annual_ret"] / 252
    sigma = info["vol"] / math.sqrt(252)
    dates = pd.bdate_range(end=datetime.today(), periods=n_days)
    lr    = np.random.normal(mu - 0.5 * sigma**2, sigma, n_days)
    pm    = np.exp(np.cumsum(lr))
    sp    = info["base"] / pm[-1]
    close = sp * pm
    return pd.DataFrame({
        "Open":   close * (1 + np.random.normal(0, 0.005, n_days)),
        "High":   close * (1 + np.abs(np.random.normal(0, 0.01, n_days))),
        "Low":    close * (1 - np.abs(np.random.normal(0, 0.01, n_days))),
        "Close":  close,
        "Volume": np.random.randint(5_000_000, 120_000_000, n_days).astype(float),
    }, index=pd.DatetimeIndex(dates, name="Date"))


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_ticker(ticker: str) -> tuple[pd.DataFrame, str]:
    try:
        import yfinance as yf
    except ImportError:
        return _dummy_series(ticker), "dummy"

    start = (datetime.today() - timedelta(days=365 * 5)).strftime("%Y-%m-%d")
    end   = (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")

    try:
        raw = yf.download(ticker, start=start, end=end,
                          auto_adjust=True, progress=False, timeout=15)
    except Exception:
        return _dummy_series(ticker), "dummy"

    if raw is None or raw.empty:
        return _dummy_series(ticker), "dummy"

    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = raw.columns.get_level_values(0)

    cols = [c for c in ["Open", "High", "Low", "Close", "Volume"] if c in raw.columns]
    df = raw[cols].copy()
    df.index = pd.to_datetime(df.index).tz_localize(None)
    df.index.name = "Date"
    df = df.dropna(subset=["Close"])
    return df, "live"


def load_all_data(tickers: list[str]) -> dict[str, tuple[pd.DataFrame, str]]:
    return {t: fetch_ticker(t) for t in tickers}


@st.cache_data(ttl=3600, show_spinner=False)
def search_ticker(query: str) -> list[dict]:
    try:
        import yfinance as yf
        results = yf.Search(query, max_results=15).quotes
        out = []
        for r in results:
            sym  = r.get("symbol", "")
            name = r.get("longname") or r.get("shortname") or sym
            exch = r.get("exchange", "")
            if sym:
                out.append({"ticker": sym, "name": name, "exchange": exch})
        return out
    except Exception:
        return []


def filter_period(df: pd.DataFrame, period: str) -> pd.DataFrame:
    if period == "YTD":
        yr = df.index.max().year
        return df[df.index.year == yr]
    if period == "Custom":
        sd = st.session_state.get("custom_start")
        ed = st.session_state.get("custom_end")
        if sd is not None and ed is not None:
            start_ts = pd.Timestamp(sd)
            end_ts   = pd.Timestamp(ed)
            result   = df[(df.index >= start_ts) & (df.index <= end_ts)]
            return result if not result.empty else df.iloc[-126:]
        return df.iloc[-126:]
    n = PERIOD_MAP.get(period)
    if n is None:
        return df
    return df.iloc[-min(n, len(df)):]


def plotly_base() -> dict:
    return dict(
        paper_bgcolor=C["bg"],
        plot_bgcolor=C["surface"],
        font=dict(family="JetBrains Mono", color=C["text"], size=12),
        xaxis=dict(
            gridcolor=C["surface_hst"], linecolor=C["border"],
            showgrid=True, zeroline=False,
            tickfont=dict(color=C["text_muted"], size=12),
            title_font=dict(color=C["text_muted"]),
        ),
        yaxis=dict(
            gridcolor=C["surface_hst"], linecolor=C["border"],
            showgrid=True, zeroline=False,
            tickfont=dict(color=C["text_muted"], size=12),
            title_font=dict(color=C["text_muted"]),
        ),
        legend=dict(
            bgcolor="rgba(0,0,0,0)", bordercolor=C["border"],
            font=dict(size=12, color=C["text"]),
        ),
        margin=dict(l=48, r=24, t=24, b=48),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor=C["surface_hi"],
            font=dict(color=C["text"], size=12, family="JetBrains Mono"),
            bordercolor=C["border"],
        ),
    )


@st.cache_data(ttl=1800, show_spinner=False)
def fetch_fear_greed() -> int:
    """
    Fear & Greed 지수 취득 우선순위:
      1. .env의 FEAR_GREED_OVERRIDE → 고정값 사용 (테스트·시연용)
      2. alternative.me 무료 API    → 키 불필요, 30분 캐시
      3. 위 둘 다 실패 시 → 50(중립) 반환
    """
    override = os.getenv("FEAR_GREED_OVERRIDE", "").strip()
    if override.isdigit():
        return max(0, min(100, int(override)))
    try:
        import urllib.request, json as _json
        with urllib.request.urlopen(
            "https://api.alternative.me/fng/?limit=1", timeout=5
        ) as resp:
            data = _json.loads(resp.read())
            return int(data["data"][0]["value"])
    except Exception:
        return 50  # 중립값 fallback


# ══════════════════════════════════════════════════════════════════════════════
# TRANSLATIONS (i18n)
# ══════════════════════════════════════════════════════════════════════════════

T_ALL = {
    "English": {
        "lang_label":             "Language",
        "data_section":           "Data",
        "live_data":              "● LIVE DATA",
        "demo_mode":              "● DEMO MODE",
        "refresh":                "🔄 Refresh",
        "add_company":            "Add Company",
        "search_placeholder":     "e.g. TSLA  or  Tesla",
        "no_results":             "No results found.",
        "btn_add":                "+ Add",
        "active_companies":       "Active Companies",
        "hide_hint":              "Uncheck to hide · ✕ to remove",
        "period":                 "Period",
        "portfolio_weights":      "Portfolio Weights (%)",
        "budget_label":           "Budget ($)",
        "weight_expander":        "⚖️ Weight Settings",
        "weight_caption":         "Enter each stock weight (%) · Recommend total = 100%",
        "total_100":              "✓ Total 100%",
        "total_under":            "Total {total}%",
        "remaining":              "Remaining",
        "total_over":             "⚠ Total {total}% — Over 100%",
        "normalized":             "(Weights normalized for simulation)",
        "unallocated":            "Unallocated",
        "notes_expander":         "📝 Watchlist Notes",
        "notes_caption":          "Jot down notes · Saved during session",
        "notes_placeholder":      "e.g. NVDA: Buy more after AI demand confirmed\nMU: Wait for dip below $120",
        "title":                  "Stock Investment Intelligence",
        "subtitle":               "Data-driven analysis for the US stock market",
        "last_data":              "Last data",
        "current_et":             "Current ET",
        "mkt_open":               "● NYSE OPEN · closes 4:00 PM ET",
        "mkt_closed_weekend":     "● NYSE CLOSED · opens Monday 9:30 AM ET",
        "mkt_closed_before":      "● NYSE CLOSED · opens today at 9:30 AM ET",
        "mkt_closed_after":       "● NYSE CLOSED · opens tomorrow 9:30 AM ET",
        "s1_title":               "① Price Trend",
        "s1_sub":                 "Closing price",
        "s2_title":               "② Cumulative Return Comparison",
        "s2_sub":                 "Normalized to 0% at period start",
        "s3_title":               "③ Annualized Volatility",
        "s3_sub":                 "σ × √252 · higher bar = higher risk",
        "s4_title":               "④ Risk vs Return",
        "s4_sub":                 "Upper-left = efficient · Lower-right = inefficient",
        "q_lr_hr":                "LOW RISK / HIGH RETURN",
        "q_hr_hr":                "HIGH RISK / HIGH RETURN",
        "q_lr_lr":                "LOW RISK / LOW RETURN",
        "q_hr_lr":                "HIGH RISK / LOW RETURN",
        "s5_title":               "⑤ Portfolio Simulator",
        "s5_sub":                 "Weighted combination of selected holdings vs individual stocks",
        "weight_warning":         "Set portfolio weights in the sidebar (must sum to > 0).",
        "stat_total_ret":         "Total Return",
        "stat_cagr":              "CAGR",
        "stat_vol":               "Volatility",
        "stat_sharpe":            "Sharpe Ratio",
        "stat_maxdd":             "Max Drawdown",
        "portfolio_label":        "Portfolio",
        "s6_title":               "⑥ Market Sentiment — Fear & Greed Index",
        "s6_sub":                 "0 = Extreme Fear · 100 = Extreme Greed · source: alternative.me",
        "fg_label":               "Fear & Greed Index",
        "fg_extreme_greed":       "Extreme Greed",
        "fg_greed":               "Greed",
        "fg_neutral":             "Neutral",
        "fg_fear":                "Fear",
        "fg_extreme_fear":        "Extreme Fear",
        "fg_min_label":           "0 Extreme Fear",
        "fg_max_label":           "100 Extreme Greed",
        "axis_vol":               "Annualized Volatility (%)",
        "axis_ret":               "Period Return (%)",
        "footer":                 "USII · Stock Investment Intelligence Dashboard",
        "not_financial":          "Not financial advice",
    },
    "한국어": {
        "lang_label":             "언어",
        "data_section":           "데이터",
        "live_data":              "● 실시간 데이터",
        "demo_mode":              "● 데모 모드",
        "refresh":                "🔄 새로고침",
        "add_company":            "기업 추가",
        "search_placeholder":     "예) TSLA  또는  Tesla",
        "no_results":             "검색 결과가 없습니다.",
        "btn_add":                "+ 추가",
        "active_companies":       "관심 기업",
        "hide_hint":              "체크 해제 시 차트에서 숨김 · ✕ 로 삭제",
        "period":                 "기간",
        "portfolio_weights":      "포트폴리오 비중 (%)",
        "budget_label":           "예산 ($)",
        "weight_expander":        "⚖️ 비중 설정",
        "weight_caption":         "각 종목 비중(%)을 직접 입력 · 합계 100% 권장",
        "total_100":              "✓ 합계 100%",
        "total_under":            "합계 {total}%",
        "remaining":              "남은 비중",
        "total_over":             "⚠ 합계 {total}% — 100% 초과",
        "normalized":             "(시뮬레이션 시 비율 정규화됨)",
        "unallocated":            "미배분",
        "notes_expander":         "📝 메모장",
        "notes_caption":          "관심 기업 메모 · 저장은 앱 세션 동안 유지됩니다",
        "notes_placeholder":      "예) NVDA: AI 수요 확인 후 추가 매수 고려\nMU: $120 이하 진입 대기",
        "title":                  "주식 투자 인텔리전스",
        "subtitle":               "미국 주식 시장 데이터 기반 분석",
        "last_data":              "최근 데이터",
        "current_et":             "현재 ET",
        "mkt_open":               "● NYSE 개장 중 · 마감 오후 4:00 ET",
        "mkt_closed_weekend":     "● NYSE 휴장 · 월요일 오전 9:30 ET 개장",
        "mkt_closed_before":      "● NYSE 휴장 · 오늘 오전 9:30 ET 개장",
        "mkt_closed_after":       "● NYSE 휴장 · 내일 오전 9:30 ET 개장",
        "s1_title":               "① 가격 추이",
        "s1_sub":                 "종가 기준",
        "s2_title":               "② 누적 수익률 비교",
        "s2_sub":                 "기간 시작 시점 기준 0% 정규화",
        "s3_title":               "③ 연환산 변동성",
        "s3_sub":                 "σ × √252 · 막대가 높을수록 위험",
        "s4_title":               "④ 위험 대비 수익률",
        "s4_sub":                 "좌상단 = 효율적 · 우하단 = 비효율적",
        "q_lr_hr":                "저위험 / 고수익",
        "q_hr_hr":                "고위험 / 고수익",
        "q_lr_lr":                "저위험 / 저수익",
        "q_hr_lr":                "고위험 / 저수익",
        "s5_title":               "⑤ 포트폴리오 시뮬레이터",
        "s5_sub":                 "선택 종목 가중 합산 vs 개별 종목",
        "weight_warning":         "사이드바에서 포트폴리오 비중을 설정하세요 (합계 > 0).",
        "stat_total_ret":         "총 수익률",
        "stat_cagr":              "연평균 수익률",
        "stat_vol":               "변동성",
        "stat_sharpe":            "샤프 지수",
        "stat_maxdd":             "최대 낙폭",
        "portfolio_label":        "포트폴리오",
        "s6_title":               "⑥ 시장 심리 — 공포·탐욕 지수",
        "s6_sub":                 "0 = 극도의 공포 · 100 = 극도의 탐욕 · 출처: alternative.me",
        "fg_label":               "공포·탐욕 지수",
        "fg_extreme_greed":       "극도의 탐욕",
        "fg_greed":               "탐욕",
        "fg_neutral":             "중립",
        "fg_fear":                "공포",
        "fg_extreme_fear":        "극도의 공포",
        "fg_min_label":           "0 극도의 공포",
        "fg_max_label":           "100 극도의 탐욕",
        "axis_vol":               "연환산 변동성 (%)",
        "axis_ret":               "기간 수익률 (%)",
        "footer":                 "USII · 주식 투자 인텔리전스 대시보드",
        "not_financial":          "투자 조언 아님",
    },
    "日本語": {
        "lang_label":             "言語",
        "data_section":           "データ",
        "live_data":              "● ライブデータ",
        "demo_mode":              "● デモモード",
        "refresh":                "🔄 更新",
        "add_company":            "銘柄を追加",
        "search_placeholder":     "例) TSLA  または  Tesla",
        "no_results":             "結果が見つかりません。",
        "btn_add":                "+ 追加",
        "active_companies":       "ウォッチリスト",
        "hide_hint":              "チェック解除で非表示 · ✕ で削除",
        "period":                 "期間",
        "portfolio_weights":      "ポートフォリオ配分 (%)",
        "budget_label":           "予算 ($)",
        "weight_expander":        "⚖️ 配分設定",
        "weight_caption":         "各銘柄の比率(%)を入力 · 合計100%推奨",
        "total_100":              "✓ 合計 100%",
        "total_under":            "合計 {total}%",
        "remaining":              "残り",
        "total_over":             "⚠ 合計 {total}% — 100%超過",
        "normalized":             "(シミュレーション時に正規化されます)",
        "unallocated":            "未配分",
        "notes_expander":         "📝 メモ帳",
        "notes_caption":          "銘柄メモ · セッション中保存されます",
        "notes_placeholder":      "例) NVDA: AI需要確認後に追加購入検討\nMU: $120以下でエントリー待機",
        "title":                  "株式投資インテリジェンス",
        "subtitle":               "米国株式市場のデータ分析",
        "last_data":              "最終データ",
        "current_et":             "現在ET",
        "mkt_open":               "● NYSE 開場中 · 午後4:00 ET 閉場",
        "mkt_closed_weekend":     "● NYSE 休場 · 月曜日 午前9:30 ET 開場",
        "mkt_closed_before":      "● NYSE 休場 · 本日 午前9:30 ET 開場",
        "mkt_closed_after":       "● NYSE 休場 · 明日 午前9:30 ET 開場",
        "s1_title":               "① 価格推移",
        "s1_sub":                 "終値ベース",
        "s2_title":               "② 累積リターン比較",
        "s2_sub":                 "期間開始時点を0%に正規化",
        "s3_title":               "③ 年率ボラティリティ",
        "s3_sub":                 "σ × √252 · 棒が高いほど高リスク",
        "s4_title":               "④ リスク対リターン",
        "s4_sub":                 "左上 = 効率的 · 右下 = 非効率的",
        "q_lr_hr":                "低リスク / 高リターン",
        "q_hr_hr":                "高リスク / 高リターン",
        "q_lr_lr":                "低リスク / 低リターン",
        "q_hr_lr":                "高リスク / 低リターン",
        "s5_title":               "⑤ ポートフォリオ・シミュレーター",
        "s5_sub":                 "加重平均ポートフォリオ vs 個別銘柄",
        "weight_warning":         "サイドバーでポートフォリオの比率を設定してください (合計 > 0)。",
        "stat_total_ret":         "総リターン",
        "stat_cagr":              "年平均成長率",
        "stat_vol":               "ボラティリティ",
        "stat_sharpe":            "シャープレシオ",
        "stat_maxdd":             "最大ドローダウン",
        "portfolio_label":        "ポートフォリオ",
        "s6_title":               "⑥ 市場心理 — 恐怖・強欲指数",
        "s6_sub":                 "0 = 極度の恐怖 · 100 = 極度の強欲 · 出典: alternative.me",
        "fg_label":               "恐怖・強欲指数",
        "fg_extreme_greed":       "極度の強欲",
        "fg_greed":               "強欲",
        "fg_neutral":             "中立",
        "fg_fear":                "恐怖",
        "fg_extreme_fear":        "極度の恐怖",
        "fg_min_label":           "0 極度の恐怖",
        "fg_max_label":           "100 極度の強欲",
        "axis_vol":               "年率ボラティリティ (%)",
        "axis_ret":               "期間リターン (%)",
        "footer":                 "USII · 株式投資インテリジェンス・ダッシュボード",
        "not_financial":          "投資アドバイスではありません",
    },
    "中文": {
        "lang_label":             "语言",
        "data_section":           "数据",
        "live_data":              "● 实时数据",
        "demo_mode":              "● 演示模式",
        "refresh":                "🔄 刷新",
        "add_company":            "添加股票",
        "search_placeholder":     "例) TSLA  或  Tesla",
        "no_results":             "未找到结果。",
        "btn_add":                "+ 添加",
        "active_companies":       "关注股票",
        "hide_hint":              "取消勾选以隐藏 · ✕ 删除",
        "period":                 "时间段",
        "portfolio_weights":      "投资组合权重 (%)",
        "budget_label":           "预算 ($)",
        "weight_expander":        "⚖️ 权重设置",
        "weight_caption":         "输入各股权重(%) · 建议总计100%",
        "total_100":              "✓ 合计 100%",
        "total_under":            "合计 {total}%",
        "remaining":              "剩余",
        "total_over":             "⚠ 合计 {total}% — 超过100%",
        "normalized":             "(模拟时将自动归一化)",
        "unallocated":            "未分配",
        "notes_expander":         "📝 备忘录",
        "notes_caption":          "股票笔记 · 会话期间保存",
        "notes_placeholder":      "例) NVDA: 确认AI需求后考虑加仓\nMU: 等待$120以下进场",
        "title":                  "股票投资智能",
        "subtitle":               "美国股市数据驱动分析",
        "last_data":              "最新数据",
        "current_et":             "当前ET",
        "mkt_open":               "● NYSE 开盘中 · 下午4:00 ET 收盘",
        "mkt_closed_weekend":     "● NYSE 休市 · 周一上午9:30 ET 开盘",
        "mkt_closed_before":      "● NYSE 休市 · 今日上午9:30 ET 开盘",
        "mkt_closed_after":       "● NYSE 休市 · 明日上午9:30 ET 开盘",
        "s1_title":               "① 价格走势",
        "s1_sub":                 "收盘价",
        "s2_title":               "② 累计收益率对比",
        "s2_sub":                 "以期间起始点为0%归一化",
        "s3_title":               "③ 年化波动率",
        "s3_sub":                 "σ × √252 · 柱越高风险越大",
        "s4_title":               "④ 风险与收益",
        "s4_sub":                 "左上 = 高效 · 右下 = 低效",
        "q_lr_hr":                "低风险 / 高收益",
        "q_hr_hr":                "高风险 / 高收益",
        "q_lr_lr":                "低风险 / 低收益",
        "q_hr_lr":                "高风险 / 低收益",
        "s5_title":               "⑤ 投资组合模拟器",
        "s5_sub":                 "加权组合收益 vs 个股收益",
        "weight_warning":         "请在侧边栏设置投资组合权重（总计 > 0）。",
        "stat_total_ret":         "总收益率",
        "stat_cagr":              "年均增长率",
        "stat_vol":               "波动率",
        "stat_sharpe":            "夏普比率",
        "stat_maxdd":             "最大回撤",
        "portfolio_label":        "投资组合",
        "s6_title":               "⑥ 市场情绪 — 恐惧贪婪指数",
        "s6_sub":                 "0 = 极度恐惧 · 100 = 极度贪婪 · 来源: alternative.me",
        "fg_label":               "恐惧贪婪指数",
        "fg_extreme_greed":       "极度贪婪",
        "fg_greed":               "贪婪",
        "fg_neutral":             "中性",
        "fg_fear":                "恐惧",
        "fg_extreme_fear":        "极度恐惧",
        "fg_min_label":           "0 极度恐惧",
        "fg_max_label":           "100 极度贪婪",
        "axis_vol":               "年化波动率 (%)",
        "axis_ret":               "期间收益率 (%)",
        "footer":                 "USII · 股票投资智能仪表板",
        "not_financial":          "非投资建议",
    },
}

# ══════════════════════════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════════════════════════

if "language" not in st.session_state:
    st.session_state.language = "English"

if "active_tickers" not in st.session_state:
    st.session_state.active_tickers = sorted(["NVDA", "AMD", "AVGO", "TSM"])

if "ticker_names" not in st.session_state:
    st.session_state.ticker_names = {t: COMPANIES[t]["name"] for t in COMPANIES}

if "watchlist_notes" not in st.session_state:
    st.session_state.watchlist_notes = ""

if "budget" not in st.session_state:
    st.session_state.budget = 10000


def get_name(ticker: str) -> str:
    return st.session_state.ticker_names.get(ticker, ticker)


# ══════════════════════════════════════════════════════════════════════════════
# LOAD DATA
# ══════════════════════════════════════════════════════════════════════════════

with st.spinner("Fetching latest market data…"):
    ALL_DATA = load_all_data(st.session_state.active_tickers)

sources = [src for _, src in ALL_DATA.values()]
overall_src = "live" if any(s == "live" for s in sources) else "dummy"


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════

# T는 sidebar 안에서 설정되지만 메인에서도 참조하므로 기본값 선언
T = T_ALL[st.session_state.language]

with st.sidebar:
    # ── 언어 선택 (최상단) ────────────────────────────────────────────────
    lang = st.selectbox(
        "🌐",
        list(T_ALL.keys()),
        index=list(T_ALL.keys()).index(st.session_state.language),
        key="lang_select",
        label_visibility="collapsed",
    )
    if lang != st.session_state.language:
        st.session_state.language = lang
        st.rerun()
    T = T_ALL[lang]

    st.markdown("## ⚡ USII")
    st.markdown(
        "<span style='font-size:11px;color:#a4e6ff;letter-spacing:0.08em;font-weight:600;'>"
        "STOCK INVESTMENT INTEL</span>",
        unsafe_allow_html=True,
    )
    st.divider()

    # ── 데이터 배지 & 새로고침 ──────────────────────────────────────────────
    st.markdown(f"### {T['data_section']}")
    col_badge, col_btn = st.columns([1, 1])
    with col_badge:
        badge_cls = "badge-live" if overall_src == "live" else "badge-dummy"
        badge_lbl = T["live_data"] if overall_src == "live" else T["demo_mode"]
        st.markdown(
            f'<span class="data-badge {badge_cls}" style="margin-top:6px;display:block;">'
            f'{badge_lbl}</span>',
            unsafe_allow_html=True,
        )
    with col_btn:
        if st.button(T["refresh"], use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    st.divider()

    # ── ① 기업 추가 검색 ──────────────────────────────────────────────────
    st.markdown(f"### {T['add_company']}")
    search_query = st.text_input(
        T["add_company"],
        placeholder=T["search_placeholder"],
        key="search_input",
        label_visibility="collapsed",
    )

    if search_query.strip():
        with st.spinner("Searching…"):
            results = search_ticker(search_query.strip())

        if results:
            with st.container(height=360):
                for r in results[:12]:
                    sym    = r["ticker"]
                    name   = r["name"]
                    already = sym in st.session_state.active_tickers
                    col_l, col_r = st.columns([3, 1])
                    with col_l:
                        _ct = C["text"]
                        _cm = C["text_muted"]
                        st.markdown(
                            f"<span style='font-size:12px;color:{_ct};"
                            f"font-family:JetBrains Mono;font-weight:700;'>{sym}</span>"
                            f"<br><span style='font-size:11px;color:{_cm};'>{name}</span>",
                            unsafe_allow_html=True,
                        )
                    with col_r:
                        if not already:
                            if st.button(T["btn_add"], key=f"add_{sym}",
                                         use_container_width=True):
                                st.session_state.active_tickers.append(sym)
                                st.session_state.active_tickers = sorted(st.session_state.active_tickers)
                                st.session_state.ticker_names[sym] = name
                                fetch_ticker.clear()
                                st.rerun()
                        else:
                            _cg = C["green"]
                            st.markdown(
                                f"<span style='color:{_cg};font-size:13px;font-weight:700;'>✓</span>",
                                unsafe_allow_html=True,
                            )
        else:
            _cm = C["text_muted"]
            st.markdown(
                f"<span style='color:{_cm};font-size:12px;'>{T['no_results']}</span>",
                unsafe_allow_html=True,
            )

    st.divider()

    # ── ② 기업 목록 (알파벳 순, 접기/펼치기, 스크롤) ──────────────────────
    active_sorted = sorted(st.session_state.active_tickers)
    with st.expander(f"{T['active_companies']} ({len(active_sorted)})", expanded=False):
        st.caption(T["hide_hint"])
        tickers_to_remove = []
        selected = []

        with st.container(height=min(len(active_sorted) * 46 + 10, 420)):
            for t in active_sorted:
                col_chk, col_name, col_del = st.columns([1, 5, 1])
                with col_chk:
                    checked = st.checkbox("", value=True, key=f"chk_{t}",
                                          label_visibility="collapsed")
                with col_name:
                    df, src = ALL_DATA.get(t, (pd.DataFrame(), "dummy"))
                    _ct = C["text"]
                    if not df.empty and len(df) > 1:
                        price = df["Close"].iloc[-1]
                        prev  = df["Close"].iloc[-2]
                        chg   = (price - prev) / prev * 100
                        chg_color = C["green"] if chg >= 0 else C["red"]
                        chg_arrow = "▲" if chg >= 0 else "▼"
                        st.markdown(
                            f"<span style='font-family:JetBrains Mono;font-size:12px;"
                            f"font-weight:700;color:{_ct};'>{t}</span>"
                            f"<span style='font-size:10px;color:{chg_color};margin-left:6px;'>"
                            f"{chg_arrow}{chg:+.1f}%</span>",
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(
                            f"<span style='font-family:JetBrains Mono;font-size:12px;"
                            f"color:{_ct};'>{t}</span>",
                            unsafe_allow_html=True,
                        )
                with col_del:
                    if st.button("✕", key=f"del_{t}", help=f"Remove {t}"):
                        tickers_to_remove.append(t)
                if checked:
                    selected.append(t)

        if tickers_to_remove:
            for t in tickers_to_remove:
                if t in st.session_state.active_tickers:
                    st.session_state.active_tickers.remove(t)
            st.rerun()

    if not selected:
        selected = sorted(st.session_state.active_tickers)
    if not selected:
        selected = ["NVDA"]

    st.divider()

    # ── 기간 ─────────────────────────────────────────────────────────────
    st.markdown(f"### {T['period']}")
    period_options = ["1M", "3M", "6M", "1Y", "3Y", "5Y", "YTD", "Custom"]
    period = st.selectbox("Timeframe", period_options, index=2,
                          label_visibility="collapsed")

    if period == "Custom":
        default_start = datetime.today() - timedelta(days=180)
        col_sd, col_ed = st.columns(2)
        with col_sd:
            custom_start = st.date_input("Start", value=default_start,
                                         max_value=datetime.today(),
                                         key="custom_start_input")
            st.session_state.custom_start = custom_start
        with col_ed:
            custom_end = st.date_input("End", value=datetime.today(),
                                       max_value=datetime.today(),
                                       key="custom_end_input")
            st.session_state.custom_end = custom_end

    st.divider()

    # ── 포트폴리오 비중 + 예산 ────────────────────────────────────────────
    st.markdown(f"### {T['portfolio_weights']}")

    budget = st.number_input(
        T["budget_label"],
        min_value=0,
        value=st.session_state.budget,
        step=500,
        key="budget_input",
    )
    st.session_state.budget = budget

    # f-string 내 dict 참조용 변수
    _ct   = C["text"]
    _cm   = C["text_muted"]
    _cp   = C["primary"]
    _cg   = C["green"]
    _cr   = C["red"]
    _co   = C["outline"]
    _csh  = C["surface_hst"]
    _cshi = C["surface_hi"]
    _cb   = C["border"]

    weights = {}
    with st.expander(T["weight_expander"], expanded=True):
        st.caption(T["weight_caption"])

        running_total = 0
        for t in selected:
            remaining_before = 100 - running_total
            prev_val = st.session_state.get(f"w_{t}", 0)
            max_allowed = min(100, remaining_before + prev_val)

            col_t, col_n = st.columns([2, 1])
            with col_t:
                alloc_str = f"  ${budget * prev_val / 100:,.0f}" if (budget > 0 and prev_val > 0) else ""
                st.markdown(
                    f"<span style='font-family:JetBrains Mono;font-size:12px;"
                    f"font-weight:700;color:{_ct};'>{t}</span>"
                    f"<span style='font-size:11px;color:{_cm};'>{alloc_str}</span>",
                    unsafe_allow_html=True,
                )
            with col_n:
                w = st.number_input(
                    f"w_{t}",
                    min_value=0,
                    max_value=100,
                    value=min(prev_val, max_allowed),
                    step=1,
                    key=f"w_{t}",
                    label_visibility="collapsed",
                )
            weights[t] = w
            running_total += w

        total_w   = sum(weights.values())
        remaining = 100 - total_w

        # 진행 바
        bar_pct = min(total_w, 100)
        bar_col = _cg if total_w == 100 else (_cr if total_w > 100 else _cp)
        st.markdown(
            f"<div style='margin-top:10px;background:{_csh};"
            f"border-radius:4px;height:6px;'>"
            f"<div style='width:{bar_pct}%;background:{bar_col};height:6px;"
            f"border-radius:4px;'></div></div>",
            unsafe_allow_html=True,
        )

        # 상태 텍스트
        if total_w == 100:
            status_html = f"<span style='color:{_cg};font-weight:700;'>{T['total_100']}</span>"
        elif total_w < 100:
            total_str = T["total_under"].format(total=total_w)
            status_html = (
                f"<span style='color:{_cp};font-weight:700;'>{total_str}</span>"
                f"&nbsp;&nbsp;"
                f"<span style='color:{_cm};'>{T['remaining']} "
                f"<b style='color:{_ct};'>{remaining}%</b></span>"
            )
        else:
            total_str = T["total_over"].format(total=total_w)
            status_html = (
                f"<span style='color:{_cr};font-weight:700;'>{total_str}</span>"
                f"&nbsp;&nbsp;"
                f"<span style='color:{_cm};'>{T['normalized']}</span>"
            )
        st.markdown(
            f"<div style='font-family:JetBrains Mono;font-size:12px;margin-top:8px;'>"
            f"{status_html}</div>",
            unsafe_allow_html=True,
        )

        # 예산 배분 요약표
        if budget > 0 and total_w > 0:
            rows_html = ""
            for t, w in weights.items():
                if w > 0:
                    alloc   = budget * w / 100
                    pct_bar = "█" * int(w / 5)
                    rows_html += (
                        f"<div style='font-family:JetBrains Mono;font-size:11px;"
                        f"display:flex;justify-content:space-between;margin-bottom:3px;'>"
                        f"<span style='color:{_cm};'>{t}&nbsp;"
                        f"<span style='color:{_co};font-size:9px;'>{pct_bar}</span></span>"
                        f"<span style='color:{_ct};font-weight:700;'>"
                        f"{w}%&nbsp;·&nbsp;${alloc:,.0f}</span></div>"
                    )
            unallocated = budget * remaining / 100 if remaining > 0 else 0
            footer_html = ""
            if unallocated > 0:
                footer_html = (
                    f"<div style='font-family:JetBrains Mono;font-size:11px;"
                    f"display:flex;justify-content:space-between;margin-top:4px;"
                    f"padding-top:4px;border-top:1px solid {_cb};'>"
                    f"<span style='color:{_cm};'>{T['unallocated']}</span>"
                    f"<span style='color:{_co};'>{remaining}%&nbsp;·&nbsp;${unallocated:,.0f}</span>"
                    f"</div>"
                )
            st.markdown(
                f"<div style='margin-top:10px;padding:8px 10px;"
                f"background:{_cshi};border-radius:6px;border:1px solid {_cb};'>"
                f"{rows_html}{footer_html}</div>",
                unsafe_allow_html=True,
            )

    st.divider()

    # ── 메모장 ────────────────────────────────────────────────────────────
    with st.expander(T["notes_expander"], expanded=False):
        st.caption(T["notes_caption"])
        notes_val = st.text_area(
            "Notes",
            value=st.session_state.watchlist_notes,
            height=200,
            placeholder=T["notes_placeholder"],
            label_visibility="collapsed",
            key="notes_area",
        )
        st.session_state.watchlist_notes = notes_val


# ══════════════════════════════════════════════════════════════════════════════
# HEADER
# ══════════════════════════════════════════════════════════════════════════════

_valid = [ALL_DATA[t][0].index.max()
          for t in st.session_state.active_tickers
          if t in ALL_DATA and not ALL_DATA[t][0].empty]
last_update = max(_valid) if _valid else datetime.today()

# Market status
now_et, is_open = get_market_status()
if is_open:
    market_html = f'<span class="market-status-open">{T["mkt_open"]}</span>'
else:
    wd = now_et.weekday()
    if wd >= 5:
        mkt_key = "mkt_closed_weekend"
    elif now_et.hour < 9 or (now_et.hour == 9 and now_et.minute < 30):
        mkt_key = "mkt_closed_before"
    else:
        mkt_key = "mkt_closed_after"
    market_html = f'<span class="market-status-closed">{T[mkt_key]}</span>'

_ct_h = C["text"]
_cm_h = C["text_muted"]
st.markdown(f"""
<h1 style='font-family:Inter;font-size:28px;font-weight:700;color:{_ct_h};
           letter-spacing:-0.02em;margin-bottom:6px;'>
  🇺🇸 {T['title']}
</h1>
<div style='margin-bottom:10px;'>{market_html}</div>
<p style='font-size:13px;color:{_cm_h};margin-bottom:16px;'>
  {T['subtitle']}
  &nbsp;·&nbsp; {T['last_data']}: {last_update.strftime('%Y-%m-%d')}
  &nbsp;·&nbsp; {T['current_et']}: {now_et.strftime('%H:%M')}
</p>
""", unsafe_allow_html=True)


# ── Ticker tape ───────────────────────────────────────────────────────────────
tape_items = []
for ticker in st.session_state.active_tickers:
    df, _ = ALL_DATA.get(ticker, (pd.DataFrame(), ""))
    if df.empty or len(df) < 2:
        continue
    price = df["Close"].iloc[-1]
    prev  = df["Close"].iloc[-2]
    chg   = (price - prev) / prev * 100
    arrow = "▲" if chg >= 0 else "▼"
    css   = "t-pos" if chg >= 0 else "t-neg"
    tape_items.append(
        f'<span class="t-sym">{ticker}</span>'
        f'<span class="{css}">{arrow} ${price:.2f} ({chg:+.2f}%)</span>'
        f'<span class="t-sep">|</span>'
    )

tape_html = "".join(tape_items)
st.markdown(
    f'<div class="ticker-tape"><div class="ticker-inner">{tape_html * 2}</div></div>',
    unsafe_allow_html=True,
)


# ── KPI Cards ─────────────────────────────────────────────────────────────────
cols = st.columns(min(len(selected), 6))
for i, ticker in enumerate(selected[:6]):
    df, _ = ALL_DATA.get(ticker, (pd.DataFrame(), "dummy"))
    if df.empty or len(df) < 2:
        continue
    price = df["Close"].iloc[-1]
    prev  = df["Close"].iloc[-2]
    chg   = (price - prev) / prev * 100
    vol_m = df["Volume"].iloc[-1] / 1e6
    arrow = "▲" if chg >= 0 else "▼"
    cls   = "kpi-pos" if chg >= 0 else "kpi-neg"
    name  = get_name(ticker)
    with cols[i % 6]:
        st.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-ticker">{ticker}</div>
          <div style="font-size:11px;color:{C['text_muted']};margin-bottom:4px;">{name}</div>
          <div class="kpi-price">${price:,.2f}</div>
          <div class="{cls}">{arrow} {chg:+.2f}% today</div>
          <div class="kpi-sub">Vol {vol_m:.1f}M</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# ① PRICE TREND
# ══════════════════════════════════════════════════════════════════════════════

period_label = period if period != "Custom" else (
    f"{st.session_state.get('custom_start', '?')} ~ {st.session_state.get('custom_end', '?')}"
)
st.markdown(f"<div class='section-header'>{T['s1_title']}</div>", unsafe_allow_html=True)
st.markdown(f"<div class='section-sub'>{T['s1_sub']} · {period_label}</div>", unsafe_allow_html=True)

fig1 = go.Figure()
for i, ticker in enumerate(selected):
    df, _ = ALL_DATA.get(ticker, (pd.DataFrame(), "dummy"))
    if df.empty:
        continue
    df_p  = filter_period(df, period)
    color = ticker_color(i)
    fill  = hex_to_rgba(color, 0.05)
    fig1.add_trace(go.Scatter(
        x=df_p.index, y=df_p["Close"],
        name=ticker, mode="lines",
        line=dict(color=color, width=2),
        fill="tozeroy", fillcolor=fill,
        hovertemplate=f"<b>{ticker}</b><br>%{{x|%Y-%m-%d}}<br>${{y:,.2f}}<extra></extra>",
    ))

layout1 = plotly_base()
layout1["height"] = 380
fig1.update_layout(**layout1)
st.plotly_chart(fig1, use_container_width=True)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# ② CUMULATIVE RETURN COMPARISON
# ══════════════════════════════════════════════════════════════════════════════

st.markdown(f"<div class='section-header'>{T['s2_title']}</div>", unsafe_allow_html=True)
st.markdown(f"<div class='section-sub'>{T['s2_sub']}</div>", unsafe_allow_html=True)

fig2 = go.Figure()
for i, ticker in enumerate(selected):
    df, _ = ALL_DATA.get(ticker, (pd.DataFrame(), "dummy"))
    if df.empty:
        continue
    df_p  = filter_period(df, period)
    cum   = (df_p["Close"] / df_p["Close"].iloc[0] - 1) * 100
    color = ticker_color(i)
    fig2.add_trace(go.Scatter(
        x=df_p.index, y=cum,
        name=f"{ticker} ({cum.iloc[-1]:+.1f}%)",
        mode="lines", line=dict(color=color, width=2),
        hovertemplate=f"<b>{ticker}</b><br>%{{x|%Y-%m-%d}}<br>%{{y:+.2f}}%<extra></extra>",
    ))

fig2.add_hline(y=0, line_dash="dot", line_color=C["border"], line_width=1)
layout2 = plotly_base()
layout2["height"] = 360
layout2["yaxis"]["ticksuffix"] = "%"
fig2.update_layout(**layout2)
st.plotly_chart(fig2, use_container_width=True)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# ③ VOLATILITY
# ══════════════════════════════════════════════════════════════════════════════

st.markdown(f"<div class='section-header'>{T['s3_title']}</div>", unsafe_allow_html=True)
st.markdown(f"<div class='section-sub'>{T['s3_sub']}</div>", unsafe_allow_html=True)

vols, annual_rets, valid_tickers = [], [], []
for ticker in selected:
    df, _ = ALL_DATA.get(ticker, (pd.DataFrame(), "dummy"))
    if df.empty:
        continue
    df_p = filter_period(df, period)
    if len(df_p) < 2:
        continue
    dr = df_p["Close"].pct_change().dropna()
    vols.append(dr.std() * math.sqrt(252) * 100)
    annual_rets.append((df_p["Close"].iloc[-1] / df_p["Close"].iloc[0] - 1) * 100)
    valid_tickers.append(ticker)

bar_colors = [
    C["green"]   if v < 35 else
    C["primary"] if v < 55 else
    C["red"]
    for v in vols
]

fig3 = go.Figure(go.Bar(
    x=valid_tickers, y=vols,
    marker_color=bar_colors,
    text=[f"{v:.1f}%" for v in vols],
    textposition="outside",
    textfont=dict(color=C["text"], size=12),
    hovertemplate="<b>%{x}</b><br>Volatility: %{y:.2f}%<extra></extra>",
))
layout3 = plotly_base()
layout3["height"] = 340
layout3["yaxis"]["ticksuffix"] = "%"
layout3["showlegend"] = False
layout3["bargap"] = 0.35
fig3.update_layout(**layout3)
st.plotly_chart(fig3, use_container_width=True)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# ④ RISK vs RETURN
# ══════════════════════════════════════════════════════════════════════════════

st.markdown(f"<div class='section-header'>{T['s4_title']}</div>", unsafe_allow_html=True)
st.markdown(f"<div class='section-sub'>{T['s4_sub']}</div>", unsafe_allow_html=True)

fig4 = go.Figure()
for i, (ticker, v, r) in enumerate(zip(valid_tickers, vols, annual_rets)):
    color = ticker_color(i)
    fig4.add_trace(go.Scatter(
        x=[v], y=[r],
        mode="markers+text",
        name=ticker,
        text=[ticker],
        textposition="top center",
        textfont=dict(color=color, size=12, family="JetBrains Mono"),
        marker=dict(size=14, color=color, line=dict(color=C["bg"], width=2)),
        hovertemplate=f"<b>{ticker}</b><br>Risk: %{{x:.1f}}%<br>Return: %{{y:+.1f}}%<extra></extra>",
    ))

if vols:
    mid_v = sum(vols) / len(vols)
    mid_r = sum(annual_rets) / len(annual_rets)
    fig4.add_vline(x=mid_v, line_dash="dot", line_color=C["border"], line_width=1)
    fig4.add_hline(y=mid_r, line_dash="dot", line_color=C["border"], line_width=1)

    for label, xf, yf, qcolor in [
        (T["q_lr_hr"], 0.25, 0.92, C["green"]),
        (T["q_hr_hr"], 0.75, 0.92, C["primary"]),
        (T["q_lr_lr"], 0.25, 0.08, C["text_muted"]),
        (T["q_hr_lr"], 0.75, 0.08, C["red"]),
    ]:
        fig4.add_annotation(
            xref="paper", yref="paper", x=xf, y=yf,
            text=label, showarrow=False,
            font=dict(size=9, color=qcolor), opacity=0.55,
        )

layout4 = plotly_base()
layout4["height"] = 420
layout4["xaxis"]["title"] = dict(text=T["axis_vol"], font=dict(color=C["outline"]))
layout4["yaxis"]["title"] = dict(text=T["axis_ret"], font=dict(color=C["outline"]))
layout4["xaxis"]["ticksuffix"] = "%"
layout4["yaxis"]["ticksuffix"] = "%"
layout4["showlegend"] = False
fig4.update_layout(**layout4)
st.plotly_chart(fig4, use_container_width=True)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# ⑤ PORTFOLIO SIMULATOR
# ══════════════════════════════════════════════════════════════════════════════

st.markdown(f"<div class='section-header'>{T['s5_title']}</div>", unsafe_allow_html=True)
st.markdown(f"<div class='section-sub'>{T['s5_sub']}</div>", unsafe_allow_html=True)

if total_w == 0:
    st.warning(T["weight_warning"])
else:
    norm_w = {t: w / total_w for t, w in weights.items() if t in selected and w > 0}

    base_series = {}
    for ticker in norm_w:
        df, _ = ALL_DATA.get(ticker, (pd.DataFrame(), "dummy"))
        if not df.empty:
            base_series[ticker] = filter_period(df, period)["Close"]

    aligned   = pd.DataFrame(base_series).dropna()
    ret_mat   = aligned.pct_change().dropna()
    w_arr     = np.array([norm_w.get(t, 0) for t in aligned.columns])
    port_daily = ret_mat.values @ w_arr
    port_cum   = (1 + port_daily).cumprod() - 1

    total_ret = port_cum[-1] * 100
    n_years   = len(port_daily) / 252
    cagr      = ((1 + port_cum[-1]) ** (1 / max(n_years, 0.01)) - 1) * 100
    port_vol  = port_daily.std() * math.sqrt(252) * 100
    sharpe    = (port_daily.mean() * 252) / (port_daily.std() * math.sqrt(252) + 1e-9)
    cum_val   = (1 + port_daily).cumprod()
    roll_max  = np.maximum.accumulate(cum_val)
    max_dd    = ((cum_val - roll_max) / roll_max * 100).min()

    # Final portfolio value if budget set
    if budget > 0:
        final_val = budget * (1 + port_cum[-1])
        profit    = final_val - budget
        profit_color = C["green"] if profit >= 0 else C["red"]
        st.markdown(
            f"<div style='background:{C['surface']};border:1px solid {C['border']};"
            f"border-radius:6px;padding:12px 16px;margin-bottom:12px;"
            f"font-family:JetBrains Mono;font-size:13px;'>"
            f"<b style='color:{C['text']};'>${budget:,}</b> → "
            f"<b style='color:{C['text']};'>${final_val:,.0f}</b> &nbsp;"
            f"<span style='color:{profit_color};'>({profit:+,.0f})</span>"
            f"</div>",
            unsafe_allow_html=True,
        )

    c1, c2, c3, c4, c5 = st.columns(5)
    for col, label, val, vcolor in [
        (c1, T["stat_total_ret"], f"{total_ret:+.1f}%", C["green"] if total_ret > 0 else C["red"]),
        (c2, T["stat_cagr"],      f"{cagr:+.1f}%",      C["green"] if cagr > 0    else C["red"]),
        (c3, T["stat_vol"],       f"{port_vol:.1f}%",   C["primary"]),
        (c4, T["stat_sharpe"],    f"{sharpe:.2f}",       C["green"] if sharpe > 1  else C["red"]),
        (c5, T["stat_maxdd"],     f"{max_dd:.1f}%",      C["red"]),
    ]:
        with col:
            st.markdown(f"""
            <div class="stat-box">
              <div class="stat-label">{label}</div>
              <div class="stat-val" style="color:{vcolor};">{val}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    fig5 = go.Figure()
    for ticker in norm_w:
        df, _ = ALL_DATA.get(ticker, (pd.DataFrame(), "dummy"))
        if df.empty:
            continue
        ind   = filter_period(df, period)["Close"]
        ind_r = (ind / ind.iloc[0] - 1) * 100
        fig5.add_trace(go.Scatter(
            x=ind.index, y=ind_r,
            name=ticker, mode="lines",
            line=dict(color=C["surface_hst"], width=1, dash="dot"),
            opacity=0.7,
            hovertemplate=f"{ticker}: %{{y:+.1f}}%<extra></extra>",
        ))

    port_dates = aligned.index[1:]
    fig5.add_trace(go.Scatter(
        x=port_dates, y=port_cum * 100,
        name=T["portfolio_label"], mode="lines",
        line=dict(color=C["primary"], width=3),
        fill="tozeroy",
        fillcolor=hex_to_rgba(C["primary"], 0.06),
        hovertemplate="Portfolio: %{y:+.2f}%<extra></extra>",
    ))
    fig5.add_hline(y=0, line_dash="dot", line_color=C["border"], line_width=1)

    layout5 = plotly_base()
    layout5["height"] = 340
    layout5["yaxis"]["ticksuffix"] = "%"
    fig5.update_layout(**layout5)
    st.plotly_chart(fig5, use_container_width=True)

    pie_col, _ = st.columns([1, 1])
    with pie_col:
        fig_pie = go.Figure(go.Pie(
            labels=list(norm_w.keys()),
            values=list(norm_w.values()),
            hole=0.55,
            marker=dict(colors=COLORS[:len(norm_w)],
                        line=dict(color=C["bg"], width=2)),
            textinfo="label+percent",
            textfont=dict(size=12, color=C["text"]),
            hovertemplate="<b>%{label}</b><br>%{percent}<extra></extra>",
        ))
        fig_pie.add_annotation(
            text=T["portfolio_label"], x=0.5, y=0.5, showarrow=False,
            font=dict(size=12, color=C["text"], family="Inter"),
        )
        fig_pie.update_layout(
            paper_bgcolor=C["bg"], plot_bgcolor=C["bg"],
            margin=dict(l=0, r=0, t=20, b=0), height=280,
            showlegend=False,
        )
        st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("<div class='divider'></div>", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# ⑥ FEAR & GREED
# ══════════════════════════════════════════════════════════════════════════════

st.markdown(f"<div class='section-header'>{T['s6_title']}</div>", unsafe_allow_html=True)
st.markdown(f"<div class='section-sub'>{T['s6_sub']}</div>", unsafe_allow_html=True)

fg_score = fetch_fear_greed()
if   fg_score >= 75: fg_mood, fg_color = T["fg_extreme_greed"], C["green"]
elif fg_score >= 55: fg_mood, fg_color = T["fg_greed"],         "#77ff62"
elif fg_score >= 45: fg_mood, fg_color = T["fg_neutral"],       C["primary"]
elif fg_score >= 25: fg_mood, fg_color = T["fg_fear"],          "#ffaba0"
else:                fg_mood, fg_color = T["fg_extreme_fear"],  C["red"]

fg_col, chart_col = st.columns([1, 2])

with fg_col:
    bar_bg   = hex_to_rgba(C["surface_hst"], 1.0)
    bar_glow = hex_to_rgba(fg_color, 0.27)
    st.markdown(f"""
    <div class="fg-container">
      <div class="fg-label">{T['fg_label']}</div>
      <div class="fg-value" style="color:{fg_color};">{fg_score}</div>
      <div class="fg-mood"  style="color:{fg_color};">{fg_mood}</div>
      <div style="margin-top:16px;background:{bar_bg};border-radius:4px;height:8px;">
        <div style="width:{fg_score}%;background:{fg_color};height:8px;border-radius:4px;
                    box-shadow:0 0 8px {bar_glow};"></div>
      </div>
      <div style="display:flex;justify-content:space-between;font-size:10px;
                  color:{C['text_muted']};margin-top:4px;font-family:'JetBrains Mono',monospace;">
        <span>{T['fg_min_label']}</span><span>{T['fg_max_label']}</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

with chart_col:
    np.random.seed(7)
    fg_dates  = pd.bdate_range(end=datetime.today(), periods=90)
    fg_series = np.clip(50 + np.cumsum(np.random.normal(0, 3, 90)), 5, 95)
    fg_series[-1] = fg_score

    fg_colors = []
    for v in fg_series:
        if   v >= 75: fg_colors.append(C["green"])
        elif v >= 55: fg_colors.append("#77ff62")
        elif v >= 45: fg_colors.append(C["primary"])
        elif v >= 25: fg_colors.append("#ffaba0")
        else:         fg_colors.append(C["red"])

    fig6 = go.Figure()
    for y0, y1, color_zone in [
        (75, 100, C["green"]), (55, 75, "#77ff62"),
        (45, 55,  C["primary"]), (25, 45, "#ffaba0"), (0, 25, C["red"]),
    ]:
        fig6.add_hrect(y0=y0, y1=y1,
                       fillcolor=hex_to_rgba(color_zone, 0.05),
                       line_width=0)

    fig6.add_trace(go.Bar(
        x=fg_dates, y=fg_series,
        marker_color=fg_colors,
        hovertemplate="%{x|%Y-%m-%d}<br>Score: %{y:.0f}<extra></extra>",
    ))
    for y_val, label in [
        (12, T["fg_extreme_fear"]), (35, T["fg_fear"]), (50, T["fg_neutral"]),
        (65, T["fg_greed"]),        (87, T["fg_extreme_greed"]),
    ]:
        fig6.add_annotation(x=fg_dates[-1], y=y_val, text=label,
                            xanchor="right", showarrow=False,
                            font=dict(size=9, color=C["text_muted"]), opacity=0.8)

    layout6 = plotly_base()
    layout6["height"] = 220
    layout6["showlegend"] = False
    layout6["margin"] = dict(l=40, r=70, t=10, b=40)
    layout6["yaxis"]["range"] = [0, 100]
    fig6.update_layout(**layout6)
    st.plotly_chart(fig6, use_container_width=True)


# ── Footer ────────────────────────────────────────────────────────────────────
src_note = {
    "live":   f"Live data via yfinance · last updated {last_update.strftime('%Y-%m-%d')}",
    "cached": f"Cached data · last updated {last_update.strftime('%Y-%m-%d')} · click Refresh",
    "dummy":  "Demo mode (yfinance not installed) · pip install yfinance",
}[overall_src]

st.markdown(f"""
<div style="margin-top:32px;padding-top:16px;border-top:1px solid {C['border']};
            font-size:10px;color:{C['text_muted']};text-align:center;
            font-family:'JetBrains Mono',monospace;letter-spacing:0.05em;">
  {T['footer']}
  · {src_note}
  · <span style="color:{C['primary']};">{T['not_financial']}</span>
</div>
""", unsafe_allow_html=True)
