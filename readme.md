# 주가 데이터 분석 프로젝트

요일별, 산업 섹터별, 시가총액 구간별로 일간 수익률을 분석하는 종합 주식 시장 분석 도구입니다.

## 프로젝트 개요

이 프로젝트는 주식 시장 데이터를 다차원적으로 분석하여 일간 가격 변동의 패턴과 트렌드를 파악합니다. 통계적 인사이트와 시각화를 생성하여 시장 행동을 이해하는 데 도움을 줍니다.

## 주요 기능

- 시가와 종가 기반 일간 수익률 계산
- 요일별 수익률 분석
- 산업 섹터별 성과 비교
- 시가총액 구간별 분석 (상위 10, 50, 100개 기업)
- 종합 통계 리포팅
- 자동 시각화 생성 (6가지 차트)

## 필요 라이브러리

- Python 3.x
- pandas
- numpy
- matplotlib
- seaborn

라이브러리 설치:
```
pip install pandas numpy matplotlib seaborn
```

## 파일 구조

- `Stock_Analysis.py` - 메인 분석 스크립트
- `데이터셋_2023148078.csv` - 주가 데이터셋
- `Sector_mapping.txt` - 산업 섹터 매핑 파일
- 생성된 차트 파일들 (PNG 형식)

## 데이터셋 형식

CSV 파일은 다음을 포함해야 합니다:
- `company_name` - 기업명
- 날짜 컬럼 형식: `DD-MM-YYYY_opening` 및 `DD-MM-YYYY_closing`

## 섹터 매핑 파일

형식: `기업명|섹터명`

예시:
```
Nvidia|Technology - Semiconductors
Microsoft|Technology - Software
Apple Inc.|Technology - Consumer Electronics
```

#으로 시작하는 줄은 주석으로 처리됩니다.

## 사용 방법

메인 스크립트를 실행하세요:
```
python Stock_Analysis.py
```

스크립트는 자동으로:
1. 데이터셋과 섹터 매핑 로드
2. 모든 기업의 일간 수익률 계산
3. 통계 분석 수행
4. 시각화 차트 생성

## 출력 결과

### 콘솔 출력
- 요일별 평균 수익률
- 섹터-요일별 성과 매트릭스
- 시가총액 구간별 통계
- 전체 통계 요약

### 생성되는 차트
1. `chart_1_weekday_returns.png` - 요일별 평균 수익률
2. `chart_2_sector_weekday_heatmap.png` - 섹터-요일별 히트맵
3. `chart_3_marketcap_returns.png` - 시가총액 구간별 수익률
4. `chart_4_sector_overall_returns.png` - 전체 섹터 성과
5. `chart_5_weekday_distribution.png` - 요일별 수익률 분포 박스플롯
6. `chart_6_sector_volatility.png` - 섹터별 변동성 비교

## 분석 구성 요소

### 1. 요일별 분석
각 요일(월요일-금요일)의 수익률 평균, 중앙값, 표준편차를 계산합니다.

### 2. 섹터별 분석
기업을 산업 섹터별로 그룹화하고 여러 요일에 걸친 성과 패턴을 분석합니다.

### 3. 시가총액 분석
최근 종가를 기준으로 기업을 구간별로 나누고 구간별 성과를 비교합니다.

### 4. 통계 요약
다음을 포함한 종합 통계를 제공합니다:
- 전체 평균 및 중앙값 수익률
- 표준편차
- 최대 및 최소 일간 수익률
- 분석된 총 데이터 포인트 수

## 참고사항

- matplotlib의 'Agg' 백엔드를 사용하여 화면 표시 없이 파일 저장
- 누락되거나 유효하지 않은 가격 데이터는 자동으로 필터링
- 날짜는 DD-MM-YYYY 형식으로 파싱
- 모든 차트는 300 DPI 해상도로 저장

## 에러 처리

다음에 대한 견고한 에러 처리 포함:
- 파일 누락 (여러 디렉토리 위치 시도)
- 유효하지 않은 데이터 항목
- 날짜 파싱 오류
- 섹터 매핑 누락 (기본값 'Unknown' 사용)

