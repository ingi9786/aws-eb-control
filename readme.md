# 프로젝트 구조

```
.
├── backend.tf         # Terraform 백엔드 설정
├── dist/              # Lambda 배포 패키지 디렉터리 (버전 관리 제외)
│   ├── create_eb.zip  # EB 환경 생성 Lambda 배포 패키지
│   ├── delete_eb.zip  # EB 환경 삭제 Lambda 배포 패키지
│   └── update_domain.zip    # EB 환경 도메인 연결 Lambda 배포 패키지
├── eventbridge/             # EventBridge 리소스 설정 모듈
│   ├── start_eb_weekday.tf  # 평일 EB 시작 EventBridge 규칙
│   ├── stop_eb_weekday.tf   # 평일 EB 중지 EventBridge 규칙
│   ├── map_created_eb.tf    # EB 생성 -> 도메인 연결 EventBridge 규칙
│   └── variables.tf         # EventBridge 모듈 변수
├── lambda/           # Lambda 함수 설정 모듈
│   ├── create_eb.tf  # EB 환경 생성 Lambda 리소스
│   ├── delete_eb.tf  # EB 환경 삭제 Lambda 리소스
│   ├── update_domain.tf # 도메인 EB 연결 Lambda 리소스
│   ├── lam_role.tf   # Lambda IAM 역할 및 정책
│   ├── outputs.tf    # Lambda 모듈 출력값
│   └── variables.tf  # Lambda 모듈 변수
├── main.tf           # 메인 Terraform 설정
├── src/              # 소스 코드 디렉터리
│   ├── create_eb.py  # EB 환경 생성 Lambda 함수 코드
│   ├── delete_eb.py  # EB 환경 삭제 Lambda 함수 코드
│   └── update_domain.py  # EB 환경 도메인 연결 Lambda 함수 코드
└── variables.tf      # 루트 레벨 변수
```

> **참고**:
- `dist/` 디렉터리는 로컬에서 생성되며 Lambda 함수의 배포 패키지를 포함합니다. 버전 관리에는 포함되지 않습니다.
- `src/`: Lambda 함수의 소스 코드 저장
  - `create_eb.py`: Elastic Beanstalk 환경 생성을 위한 Python 스크립트
  - `delete_eb.py`: Elastic Beanstalk 환경 삭제를 위한 Python 스크립트
  - `update_domain.py`: Elastic Beanstalk 환경 도메인 맵핑을 위한 Python 스크립트
- `lambda/`: Terraform Lambda 모듈
  - `lam_role.tf`: Lambda 함수에 필요한 공통 IAM 역할과 정책 정의
  - `create_eb.tf`: EB 생성 Lambda 함수 리소스 정의
  - `delete_eb.tf`: EB 삭제 Lambda 함수 리소스 정의
  - `update_domain.tf`: 생성된 EB와 CNAME record 맵핑하는 함수 리소스 정의
- `eventbridge/`: Terraform EventBridge 모듈
  - `start_eb_weekday.tf`: 평일 아침 EB 환경 시작 규칙
  - `stop_eb_weekday.tf`: 평일 저녁 EB 환경 중지 규칙
  - `map_created_eb.tf`: EB 환경 생성 시 도메인 연결 규칙