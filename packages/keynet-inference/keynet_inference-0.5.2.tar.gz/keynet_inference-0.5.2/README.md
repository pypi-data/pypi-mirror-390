# keynet-inference

MLflow와 Triton Inference Server를 연동하여, Python 함수를 손쉽게 추론 API로 배포하고 실행하기 위한 라이브러리입니다.

## 설치

```bash
pip install keynet-inference
```

## 주요 개념

`keynet-inference`는 추론 파이프라인을 구성하는 몇 가지 핵심 컴포넌트를 제공합니다.

- **`@keynet_function(name)`**: 일반 Python 함수를 Keynet 추론 워크플로우의 **진입점(entrypoint)**으로 만들어주는 데코레이터입니다. 이 데코레이터는 다음과 같은 역할을 자동으로 처리합니다.

  - 함수 실행에 필요한 환경변수 로드
  - 사용자 입력을 `UserInput` 싱글톤 객체에 설정
  - 함수의 시그니처 및 반환 값 검증

- **`UserInput`**: 추론 실행 시 사용자가 전달한 입력 파라미터에 안전하게 접근할 수 있는 **싱글톤(Singleton) 객체**입니다. `UserInput.get("param_name", default_value)` 형태로 사용하며, 환경변수와 분리되어 사용자 입력만을 명확하게 관리할 수 있습니다.

- **`TritonPlugin`**: MLflow 모델 레지스트리에 등록된 모델을 사용하여 Triton Inference Server에 추론 요청을 보내는 클라이언트입니다. 복잡한 Triton API 호출을 단순화하여, 모델 이름과 입력 데이터만으로 쉽게 예측을 수행할 수 있습니다.

- **`Storage`**: S3, MinIO 등 오브젝트 스토리지와의 파일 상호작용을 추상화한 인터페이스입니다. 추론에 필요한 이미지나 데이터를 다운로드하거나, 결과 파일을 업로드하는 작업을 간편하게 처리합니다.

## 사용 예제

### 전체 추론 파이프라인

다음은 `Storage`에서 이미지를 다운로드하고, 전처리한 뒤 Triton으로 추론하고, 결과를 다시 `Storage`에 업로드하는 전체 워크플로우 예제입니다.

> **참고**: 아래 예제에서 `main` 함수는 `args` 파라미터를 받지만, 실제 사용자 입력값은 `UserInput.get()` 메소드를 통해 접근하는 것을 권장합니다. `@keynet_function` 데코레이터가 `args`를 사용하여 `UserInput` 싱글톤을 내부적으로 초기화하므로, 코드의 명확성과 일관성을 위해 `UserInput`을 사용하세요.

```python
import numpy as np
from PIL import Image
from io import BytesIO
from keynet_inference import keynet_function, UserInput, TritonPlugin, Storage

# 1. @keynet_function으로 추론 함수 정의
# "image-detection"은 이 함수의 고유 이름으로 사용됩니다.
@keynet_function("image-detection")
def main(args: dict):
    # Storage 및 TritonPlugin 클라이언트 초기화
    # 관련 설정(예: 엔드포인트, 자격 증명)은 환경변수에서 자동으로 로드됩니다.
    storage = Storage()
    triton = TritonPlugin()

    # 2. 사용자 입력 파라미터 가져오기
    # UserInput.get()을 사용하여 안전하게 입력에 접근합니다.
    image_url = UserInput.get("image_url")
    threshold = UserInput.get("threshold", 0.5)  # 기본값 0.5 설정

    # 3. 입력 데이터 처리 (Storage에서 다운로드)
    image_buffer = storage.get(image_url)
    image = Image.open(image_buffer).convert("RGB")

    # 4. 모델 추론을 위한 전처리
    input_tensor = preprocess(image, size=(640, 640))

    # 5. Triton Inference Server로 추론 요청
    outputs = triton.predict(
        df={"input_0": input_tensor}
    )

    # 6. 추론 결과 후처리
    result_image_buffer = postprocess(outputs["output_0"], image, threshold)

    # 7. 결과물을 Storage에 업로드
    url = storage.put(result_image_buffer)

    # 8. 결과 반환 (JSON 직렬화 가능해야 함)
    return {"url": url}

def preprocess(image: Image.Image, size: tuple) -> np.ndarray:
    """이미지를 모델 입력 형식에 맞게 전처리합니다."""
    resized = image.resize(size)
    array = np.array(resized, dtype=np.float32) / 255.0
    array = array.transpose(2, 0, 1)  # HWC -> CHW
    return np.expand_dims(array, axis=0)

def postprocess(outputs: np.ndarray, original_image: Image.Image, threshold: float) -> BytesIO:
    """추론 결과를 원본 이미지에 시각화하고 이미지 버퍼를 반환합니다."""
    # 예시: threshold를 사용한 바운딩 박스 필터링 및 그리기 로직
    # (실제 구현은 모델 출력에 따라 달라집니다)
    # ...

    buffer = BytesIO()
    original_image.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer
```

## Python 버전 지원

Python 3.9, 3.10, 3.11, 3.12

## 라이선스

MIT License
