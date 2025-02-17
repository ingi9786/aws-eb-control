# 프로젝트 구조

```
.
├── backend.tf          # Terraform 백엔드 설정
├── eventbridge/        # EventBridge 리소스 설정 모듈
│   ├── start_eb_weekday.tf  # 평일 EB 시작 EventBridge 규칙
│   └── variables.tf    # EventBridge 모듈 변수
├── lambda/            # Lambda 함수 설정 모듈
│   ├── create_eb.tf   # EB 환경 생성 Lambda 리소스
│   ├── outputs.tf     # Lambda 모듈 출력값
│   ├── test.tf        # 테스트 관련 Lambda 리소스
│   └── variables.tf   # Lambda 모듈 변수
├── main.tf            # 메인 Terraform 설정
├── src/               # 소스 코드 디렉터리
│   ├── create_eb.py   # EB 환경 생성 Lambda 함수 코드
│   └── test_lambda.py # 테스트 Lambda 함수 코드
└── variables.tf       # 루트 레벨 변수
```

> **참고**:
- `dist/` 디렉터리는 로컬에서 생성되며 Lambda 함수의 배포 패키지를 포함합니다. 버전 관리에는 포함되지 않습니다.
- `src/`: Lambda 함수의 소스 코드 저장
  - `create_eb.py`: Elastic Beanstalk 환경 생성을 위한 Python 스크립트