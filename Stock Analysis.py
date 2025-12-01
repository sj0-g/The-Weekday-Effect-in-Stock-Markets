import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
import os
warnings.filterwarnings('ignore')

# 폰트 설정
plt.rcParams['axes.unicode_minus'] = False

def load_sector_mapping(filepath='sector_mapping.txt'):
    """sector_mapping.txt 파일에서 섹터 정보 로드"""
    sector_map = {}
    
    # 스크립트와 같은 디렉토리에서 파일 찾기
    script_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()
    full_path = os.path.join(script_dir, filepath)
    
    # 현재 디렉토리에도 확인
    if not os.path.exists(full_path):
        full_path = filepath
    
    if not os.path.exists(full_path):
        print(f"⚠️  경고: {filepath} 파일을 찾을 수 없습니다.")
        print(f"찾은 위치: {script_dir}")
        print("기본 섹터 분류를 사용합니다.")
        return None
    
    filepath = full_path
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # 주석 및 빈 줄 무시
            if line.startswith('#') or not line:
                continue
            
            # 회사명|섹터명 파싱
            if '|' in line:
                company, sector = line.split('|', 1)
                sector_map[company] = sector
    
    print(f"✅ {len(sector_map)}개 기업의 섹터 정보를 로드했습니다.")
    return sector_map

# 스크립트와 같은 디렉토리 찾기
script_dir = os.path.dirname(os.path.abspath(__file__)) if '__file__' in globals() else os.getcwd()

# CSV 파일 읽기 (여러 위치 시도)
csv_filename = '데이터셋_2023148078.csv'
csv_paths_to_try = [
    os.path.join(script_dir, csv_filename),  # 스크립트와 같은 디렉토리
    csv_filename,  # 현재 디렉토리
    '/mnt/user-data/uploads/' + csv_filename,  # uploads 폴더
]

csv_path = None
for path in csv_paths_to_try:
    if os.path.exists(path):
        csv_path = path
        break

if csv_path is None:
    raise FileNotFoundError(f"{csv_filename} 파일을 찾을 수 없습니다. 다음 위치를 확인했습니다: {csv_paths_to_try}")

print(f"CSV 파일 로드: {csv_path}")
df = pd.read_csv(csv_path)

# 섹터 매핑 로드
sector_mapping = load_sector_mapping('sector_mapping.txt')

# 데이터 전처리
def prepare_data(df, sector_mapping):
    """데이터 준비 및 전처리"""
    if sector_mapping:
        df['sector'] = df['company_name'].map(sector_mapping)
    else:
        df['sector'] = 'Unknown'
    
    # 날짜 열 추출
    date_columns = [col for col in df.columns if '_opening' in col or '_closing' in col]
    dates = sorted(list(set([col.split('_')[0] for col in date_columns])))
    
    return df, dates

def calculate_daily_returns(df, dates):
    """일별 수익률 계산"""
    returns_data = []
    
    for idx, row in df.iterrows():
        company = row['company_name']
        sector = row['sector']
        
        for date in dates:
            opening_col = f"{date}_opening"
            closing_col = f"{date}_closing"
            
            if opening_col in df.columns and closing_col in df.columns:
                opening = row[opening_col]
                closing = row[closing_col]
                
                if pd.notna(opening) and pd.notna(closing) and opening > 0:
                    daily_return = ((closing - opening) / opening) * 100
                    
                    try:
                        date_obj = datetime.strptime(date, '%d-%m-%Y')
                        weekday = date_obj.strftime('%A')
                        weekday_short = {
                            'Monday': 'Mon',
                            'Tuesday': 'Tue',
                            'Wednesday': 'Wed',
                            'Thursday': 'Thu',
                            'Friday': 'Fri',
                            'Saturday': 'Sat',
                            'Sunday': 'Sun'
                        }
                        
                        returns_data.append({
                            'company': company,
                            'sector': sector,
                            'date': date_obj,
                            'weekday': weekday_short[weekday],
                            'daily_return': daily_return
                        })
                    except:
                        continue
    
    return pd.DataFrame(returns_data)

def analyze_by_weekday(returns_df):
    """요일별 수익률 분석"""
    weekday_order = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
    
    weekday_returns = returns_df.groupby('weekday')['daily_return'].agg(['mean', 'median', 'std'])
    weekday_returns = weekday_returns.reindex(weekday_order)
    
    print("\n=== 요일별 평균 주가 상승률 ===")
    print(weekday_returns)
    
    return weekday_returns

def analyze_by_sector_weekday(returns_df):
    """산업 섹터별, 요일별 수익률 분석"""
    sector_weekday_returns = returns_df.groupby(['sector', 'weekday'])['daily_return'].mean().reset_index()
    sector_weekday_pivot = sector_weekday_returns.pivot(index='sector', columns='weekday', values='daily_return')
    
    weekday_order = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
    sector_weekday_pivot = sector_weekday_pivot[weekday_order]
    
    print("\n=== 산업 섹터별 요일별 평균 수익률 (%) ===")
    print(sector_weekday_pivot)
    
    return sector_weekday_pivot

def analyze_by_marketcap(df, returns_df, top_n_list=[10, 50, 100]):
    """시가총액 구간별 수익률 분석"""
    latest_date = [col for col in df.columns if '_closing' in col][-1]
    df['latest_price'] = df[latest_date]
    df_sorted = df.sort_values('latest_price', ascending=False).reset_index(drop=True)
    
    results = {}
    
    for top_n in top_n_list:
        if top_n <= len(df_sorted):
            top_companies = df_sorted.head(top_n)['company_name'].tolist()
            top_returns = returns_df[returns_df['company'].isin(top_companies)]
            
            avg_return = top_returns['daily_return'].mean()
            median_return = top_returns['daily_return'].median()
            
            results[f'Top {top_n}'] = {
                'mean': avg_return,
                'median': median_return,
                'count': len(top_returns)
            }
            
            print(f"\n=== Top {top_n} 기업 평균 수익률 ===")
            print(f"평균 수익률: {avg_return:.4f}%")
            print(f"중앙값 수익률: {median_return:.4f}%")
            print(f"데이터 포인트 수: {len(top_returns)}")
    
    return results, df_sorted

def visualize_results(weekday_returns, sector_weekday_pivot, marketcap_results, returns_df):
    """결과 시각화 - 각 차트를 개별 파일로 저장"""
    
    # 1. 요일별 평균 수익률
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    weekday_returns['mean'].plot(kind='bar', ax=ax1, color='steelblue')
    ax1.set_title('Average Daily Returns by Weekday', fontsize=16, fontweight='bold')
    ax1.set_xlabel('Weekday', fontsize=12)
    ax1.set_ylabel('Average Return (%)', fontsize=12)
    ax1.axhline(y=0, color='r', linestyle='--', linewidth=0.8)
    ax1.grid(True, alpha=0.3)
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
    plt.tight_layout()
    plt.savefig('chart_1_weekday_returns.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✅ chart_1_weekday_returns.png 저장 완료")
    
    # 2. 산업 섹터별 요일별 히트맵 (세로로 길게)
    num_sectors = len(sector_weekday_pivot)
    fig_height = max(12, num_sectors * 0.4)  # 섹터가 많으면 세로로 길게
    
    fig2, ax2 = plt.subplots(figsize=(12, fig_height))
    sns.heatmap(sector_weekday_pivot, annot=True, fmt='.2f', cmap='RdYlGn', 
                center=0, ax=ax2, cbar_kws={'label': 'Return (%)'}, 
                annot_kws={'fontsize': 8})
    ax2.set_title('Average Returns by Sector and Weekday', fontsize=16, fontweight='bold', pad=20)
    ax2.set_xlabel('Weekday', fontsize=12)
    ax2.set_ylabel('Sector', fontsize=12)
    ax2.tick_params(axis='y', labelsize=9)
    plt.tight_layout()
    plt.savefig('chart_2_sector_weekday_heatmap.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✅ chart_2_sector_weekday_heatmap.png 저장 완료")
    
    # 3. 시가총액 구간별 평균 수익률
    fig3, ax3 = plt.subplots(figsize=(10, 6))
    marketcap_means = [v['mean'] for v in marketcap_results.values()]
    marketcap_labels = list(marketcap_results.keys())
    bars = ax3.bar(marketcap_labels, marketcap_means, color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
    ax3.set_title('Average Returns by Market Cap Group', fontsize=16, fontweight='bold')
    ax3.set_xlabel('Market Cap Group', fontsize=12)
    ax3.set_ylabel('Average Return (%)', fontsize=12)
    ax3.axhline(y=0, color='r', linestyle='--', linewidth=0.8)
    ax3.grid(True, alpha=0.3, axis='y')
    
    # 값 표시
    for bar in bars:
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.3f}%', ha='center', va='bottom' if height > 0 else 'top', fontsize=10)
    
    plt.tight_layout()
    plt.savefig('chart_3_marketcap_returns.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✅ chart_3_marketcap_returns.png 저장 완료")
    
    # 4. 섹터별 평균 수익률 (세로로 매우 길게)
    sector_returns = sector_weekday_pivot.mean(axis=1).sort_values(ascending=True)
    fig_height = max(10, len(sector_returns) * 0.35)
    
    fig4, ax4 = plt.subplots(figsize=(10, fig_height))
    bars = sector_returns.plot(kind='barh', ax=ax4, color='coral')
    ax4.set_title('Average Returns by Sector (Overall)', fontsize=16, fontweight='bold')
    ax4.set_xlabel('Average Return (%)', fontsize=12)
    ax4.set_ylabel('Sector', fontsize=12)
    ax4.axvline(x=0, color='r', linestyle='--', linewidth=0.8)
    ax4.grid(True, alpha=0.3, axis='x')
    ax4.tick_params(axis='y', labelsize=9)
    plt.tight_layout()
    plt.savefig('chart_4_sector_overall_returns.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✅ chart_4_sector_overall_returns.png 저장 완료")
    
    # 5. 요일별 수익률 박스플롯
    fig5, ax5 = plt.subplots(figsize=(12, 7))
    returns_df_copy = returns_df.copy()
    weekday_order = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
    returns_df_copy['weekday'] = pd.Categorical(returns_df_copy['weekday'], 
                                                  categories=weekday_order, 
                                                  ordered=True)
    returns_df_copy = returns_df_copy.sort_values('weekday')
    
    sns.boxplot(data=returns_df_copy, x='weekday', y='daily_return', ax=ax5, palette='Set2')
    ax5.set_title('Distribution of Returns by Weekday', fontsize=16, fontweight='bold')
    ax5.set_xlabel('Weekday', fontsize=12)
    ax5.set_ylabel('Daily Return (%)', fontsize=12)
    ax5.axhline(y=0, color='r', linestyle='--', linewidth=0.8)
    ax5.grid(True, alpha=0.3, axis='y')
    plt.setp(ax5.xaxis.get_majorticklabels(), rotation=0)
    plt.tight_layout()
    plt.savefig('chart_5_weekday_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✅ chart_5_weekday_distribution.png 저장 완료")
    
    # 6. 섹터별 변동성 (세로로 매우 길게)
    sector_volatility = returns_df.groupby('sector')['daily_return'].std().sort_values(ascending=True)
    fig_height = max(10, len(sector_volatility) * 0.35)
    
    fig6, ax6 = plt.subplots(figsize=(10, fig_height))
    sector_volatility.plot(kind='barh', ax=ax6, color='lightblue')
    ax6.set_title('Volatility by Sector (Std Dev)', fontsize=16, fontweight='bold')
    ax6.set_xlabel('Standard Deviation (%)', fontsize=12)
    ax6.set_ylabel('Sector', fontsize=12)
    ax6.grid(True, alpha=0.3, axis='x')
    ax6.tick_params(axis='y', labelsize=9)
    plt.tight_layout()
    plt.savefig('chart_6_sector_volatility.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("✅ chart_6_sector_volatility.png 저장 완료")
    
    print("\n✅ 총 6개의 차트가 개별 파일로 저장되었습니다!")
    print("  - chart_1_weekday_returns.png")
    print("  - chart_2_sector_weekday_heatmap.png")
    print("  - chart_3_marketcap_returns.png")
    print("  - chart_4_sector_overall_returns.png")
    print("  - chart_5_weekday_distribution.png")
    print("  - chart_6_sector_volatility.png")

# 메인 실행
if __name__ == "__main__":
    print("=" * 60)
    print("주가 데이터 분석 시작")
    print("=" * 60)
    
    # 데이터 준비
    df, dates = prepare_data(df, sector_mapping)
    print(f"\n분석 기간: {len(dates)}일")
    print(f"분석 기업 수: {len(df)}")
    
    # 일별 수익률 계산
    returns_df = calculate_daily_returns(df, dates)
    print(f"\n총 데이터 포인트 수: {len(returns_df)}")
    
    # 요일별 분석
    weekday_returns = analyze_by_weekday(returns_df)
    
    # 섹터별 요일별 분석
    sector_weekday_pivot = analyze_by_sector_weekday(returns_df)
    
    # 시가총액 구간별 분석
    marketcap_results, df_sorted = analyze_by_marketcap(df, returns_df)
    
    # 시각화
    visualize_results(weekday_returns, sector_weekday_pivot, marketcap_results, returns_df)
    
    # 추가 통계
    print("\n=== 전체 통계 ===")
    print(f"전체 평균 일간 수익률: {returns_df['daily_return'].mean():.4f}%")
    print(f"전체 중앙값 일간 수익률: {returns_df['daily_return'].median():.4f}%")
    print(f"전체 표준편차: {returns_df['daily_return'].std():.4f}%")
    print(f"최대 일간 수익률: {returns_df['daily_return'].max():.4f}%")
    print(f"최소 일간 수익률: {returns_df['daily_return'].min():.4f}%")
    
    print("\n" + "=" * 60)
    print("분석 완료!")
    print("=" * 60)