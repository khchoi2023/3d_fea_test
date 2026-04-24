# 3D Cantilever Static FEA Test Program

## 1. 프로젝트 개요

이 프로젝트는 Python으로 3D 외팔보(cantilever beam) 모델을 자동 생성하고, TET4(4절점 사면체) 요소를 사용한 3차원 선형 정적 유한요소해석을 수행한 뒤, von Mises 응력을 3D 솔리드 모델 위에 컬러맵으로 표시하는 테스트용 프로그램입니다.

PyVista/VTK 기반 인터랙티브 뷰어를 사용하므로 사용자는 마우스 드래그로 모델을 회전하고, 마우스 휠로 확대/축소하며 결과를 확인할 수 있습니다.

## 2. 목적

- Python 기반 3D FEA 테스트 워크플로우 구현
- 외팔보의 3D 선형 정적해석 예제 제공
- von Mises 응력 후처리 및 인터랙티브 시각화 제공
- Windows 탐색기에서 배치파일 더블클릭만으로 실행 가능한 환경 제공

## 3. 해석 대상

- 형상: 3D 직육면체 외팔보
- 치수:
  - 길이 `L = 1000 mm`
  - 폭 `B = 80 mm`
  - 높이 `H = 120 mm`
- 재질:
  - Steel
  - 탄성계수 `E = 200000 MPa`
  - 포아송비 `nu = 0.3`
- 경계조건:
  - `x = 0` 면 전체 고정
- 하중조건:
  - `x = L` 면에 총 하중 `1000 N`
  - `-Z` 방향으로 균등 분배
- 단위계:
  - `mm`, `N`, `MPa`

## 4. 사용 기술

- Python
- NumPy
- SciPy
- PyVista
- VTK
- TET4 element

## 5. 설치 방법

Windows에서는 아래 배치파일을 사용합니다.

## 6. Windows에서 실행하는 방법

처음 한 번만 아래 순서대로 실행합니다.

1. `00_create_venv.bat` 더블클릭
   - 프로젝트 전용 Python 가상환경을 생성합니다.
2. `01_install_requirements.bat` 더블클릭
   - 필요한 Python 패키지를 설치합니다.
3. `02_run_analysis.bat` 더블클릭
   - 3D 외팔보 정적해석을 실행합니다.
   - 결과 파일이 `results` 폴더에 저장됩니다.
4. `03_open_viewer.bat` 더블클릭
   - 저장된 해석 결과를 다시 열어 3D 인터랙티브 뷰어로 확인합니다.
   - 마우스 드래그로 모델을 회전할 수 있습니다.
   - 마우스 휠로 확대/축소할 수 있습니다.

한 번에 전체 과정을 실행하려면:

- `04_run_all.bat` 더블클릭

단, 처음 실행 시 패키지 설치 시간이 걸릴 수 있습니다.

## 7. 수동 실행 방법

```bat
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m src.main
```

## 8. 결과 확인 방법

- `results` 폴더의 PNG 이미지 확인
- PyVista 인터랙티브 창에서 마우스 드래그로 회전
- 마우스 휠로 확대/축소
- 오른쪽 컬러바로 von Mises 응력 확인
- `3d_cantilever_result.vtu` 파일을 ParaView 또는 PyVista로 확인 가능

## 9. 현재 한계

- 테스트용 코드입니다.
- 상용 FEA 수준 정확도를 목표로 하지 않습니다.
- TET4 저차 요소를 사용합니다.
- 접촉, 비선형, 소성, 대변형을 지원하지 않습니다.
- 자동 CAD import를 지원하지 않습니다.
- 응력 smoothing은 단순 평균 방식입니다.
- 거친 메쉬와 저차 요소 특성상 이론값과 차이가 날 수 있습니다.

## 10. 향후 개선 방향

- SolidWorks STEP 파일 import
- Gmsh 연동
- Physical Group 기반 경계조건 지정
- 3D GUI에서 면 클릭으로 고정/하중 지정
- HEX8 요소 추가
- 응력 smoothing 개선
- 안전율 계산
- PDF 보고서 자동 생성
- STL/VTK/VTU export 개선
- 여러 하중 케이스 지원
- 재질 DB 추가

향후 STEP 기반 CAD import를 추가할 때는 `pythonocc-core`, `cadquery`, `gmsh` 또는 별도 mesher를 연동하여 형상 읽기 -> 체적 메쉬 생성 -> 면 그룹 인식 -> 경계조건 지정 순서로 확장할 수 있습니다.
