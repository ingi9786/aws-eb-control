### 개요
> 이 프로젝트는 특정 시간 동안만 Elastic Beanstalk(EB) 환경을 운영하도록 설정된 레포지토리입니다.
> 기본적으로 KST 기준 평일 (09:00~22:00) 동안 EB 환경이 실행되며, 그 외 시간에는 자동으로 중지됩니다.
>
> 인프라 구성 변수는 terraform.tfvars 에서 변수로 관리됩니다.
> 프로젝트별 운영 시간을 변경하려면 변수 값을 수정한 후 새로운 EventBridge 규칙을 생성해야합니다.

---

### 프로젝트 구조

```
.
├── backend.tf         # Terraform 백엔드 설정
├── dist/              # Lambda 배포 패키지 디렉터리 (버전 관리 제외)
│   ├── create_eb.zip  # EB 환경 생성 Lambda 배포 패키지
│   ├── delete_eb.zip  # EB 환경 삭제 Lambda 배포 패키지
│   └── postdeploy_eb.zip    # EB 환경 도메인 연결 Lambda 배포 패키지
├── eventbridge/             # EventBridge 리소스 설정 모듈
│   ├── start_eb_weekday.tf  # 평일 EB 시작 EventBridge 규칙
│   ├── stop_eb_weekday.tf   # 평일 EB 중지 EventBridge 규칙
│   ├── setup_after_start_eb.tf   # EB 생성 완료 시 추가 테스트 규칙
│   └── variables.tf         # EventBridge 모듈 변수
├── lambda/           # Lambda 함수 설정 모듈
│   ├── create_eb.tf  # EB 환경 생성 Lambda 리소스
│   ├── delete_eb.tf  # EB 환경 삭제 Lambda 리소스
│   ├── postdeploy_eb.tf # 도메인 EB 연결 및 waf associate Lambda 리소스
│   ├── lam_role.tf   # Lambda IAM 역할 및 정책
│   ├── outputs.tf    # Lambda 모듈 출력값
│   └── variables.tf  # Lambda 모듈 변수
├── main.tf           # 메인 Terraform 설정
├── src/              # 소스 코드 디렉터리
│   ├── create_eb.py  # EB 환경 생성 Lambda 함수 코드
│   ├── delete_eb.py  # EB 환경 삭제 Lambda 함수 코드
│   └── postdeploy_eb.py  # EB 생성 후속 작업 Lambda 함수 코드
└── variables.tf      # 루트 레벨 변수
```

> **참고**:
- `dist/` 디렉터리는 로컬에서 생성되며 Lambda 함수의 배포 패키지를 포함합니다. 버전 관리에는 포함되지 않습니다.
- `src/`: Lambda 함수의 소스 코드 저장
  - `create_eb.py`: Elastic Beanstalk 환경 생성을 위한 Python 스크립트
  - `delete_eb.py`: Elastic Beanstalk 환경 삭제를 위한 Python 스크립트
  - `postdeploy_eb.py`: Elastic Beanstalk 환경 도메인 맵핑 및 waf 연결을 위한 Python 스크립트
- `lambda/`: Terraform Lambda 모듈
  - `lam_role.tf`: Lambda 함수에 필요한 공통 IAM 역할과 정책 정의
  - `create_eb.tf`: EB 생성 Lambda 함수 리소스 정의
  - `delete_eb.tf`: EB 삭제 Lambda 함수 리소스 정의
  - `postdeploy_eb.tf`: 생성된 EB와 CNAME record 맵핑 및 waf 연결하는 함수 리소스 정의
- `eventbridge/`: Terraform EventBridge 모듈
  - `start_eb_weekday.tf`: 평일 아침 EB 환경 시작 규칙
  - `stop_eb_weekday.tf`: 평일 저녁 EB 환경 중지 규칙
  - `setup_after_start_eb.tf`: EB 환경 생성 후 도메인 연결 및 waf 연결 규칙

