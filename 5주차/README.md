# 5주차 위클리 챌린지
--
## 위클리 챌린지 #1~4

### 1~3번에서 사용된 데이터 셋 : CIFAR-10 
#### 정규화
- ImageNet으로 사전 학습된 모델이기 때문에 Imagenet의 평균과 표준편차로 정규화
- ImageNet (R,G,B) 평균 : 0.485, 0.456, 0.406
- ImageNet (R,G,B) std : 0.229, 0.224, 0.225

### Hyperparameter
num_epochs : 10
batch_size : 64

---- 
### 1. ResNet 모델을 불러와 새로운 이미지 데이터셋을 분류하세요.
---
#### 방법 1. Training from scratch
- 사전 학습 모델의 구조만 가져오고 학습된 가중치는 가져오지 않는다.
- 1. 구조를 가져옴
- 2. 레이어를 알맞게 수정

1) ResNet50
- 구조 변경 : 하위 두개의 레이어를 제거 후 Average Pooling 레이어와 FCL 레이어 2개를 추가
- 실험 결과
	- ResNet50 Test Accuracy: 48.30%
	- 학습 시간 : 10:30
##### 문제점
- 구조만 가져오고 가중치를 사용하지 않았더니 성능이 심각하게 안 좋은 결과.
- Loss값 또한 거의 줄어들지 못함. 
- 추세를 보아하니 천천히 수렴중인듯 하여 epoch 수를 늘린다면 개선될 것 같다.

#### 방법 2. Full Fine Tuning
- 가중치를 갖고 온 후 시작점으로 삼고, 가중치를 모두 다시 학습시킨다.
- 1. 구조와 pretrained weight를 갖고 옴
- 2. ResNet 구조의 마지막 FCL 부분만 CIFAR-10의 클래스 개수에 맞춰서 변경

1) ResNet18
- 실험 결과
	- ResNet18 Test Accuracy: 81.10%

2) ResNet50
- 실험 결과
	- ResNet50 Test Accuracy: 84.68%
	- 학습 시간 : 10:24 (10 epoch)

#### 개선된 점
- 사전 학습된 가중치를 사용하자 안정적으로 Loss값이 줄어들었고 성능 또한 대폭 향상되었다.

#### 문제점
- ResNet18 또는 ResNet50 의 네트워크 구조를 그대로 사용하면 ImageNet과 인풋 사이즈가 다르기 때문에 의도된대로 학습이 잘 되지 않는다. 
- ImageNet의 경우 224x224 -> convolution 레이어 통과 후 최종 크기 7x7 : 인풋의 $1/32$이 됨
- CIFAR-10의 경우 32x32 -> 1x1 이 되어버리기 때문에 이 다음에 average pool을 하는 의미가 사라지게 됨.


#### 방법 3. 레이어를 CIFAR-10 인풋에 맞춰 수정
- [Claude의 조언](https://claude.ai/share/ef757cf6-721e-4e7b-bc66-1bf275b8806c)
- 1) Conv1을 kernel size 3, padding 1로 수정 
- 2) maxpool레이어를 제거하고 Identity레이어로 교체하여 그대로 넘겨줌
- 3) ResNet 구조의 마지막 FCL 부분을 CIFAR-10의 클래스 개수에 맞춰서 변경

```
Input         (batch,    3, 32, 32)
conv1 (수정)   (batch,   64, 32, 32)  ← 크기 유지
maxpool 제거   (batch,   64, 32, 32)  ← 유지
layer1        (batch,  256, 32, 32)
layer2        (batch,  512, 16, 16)
layer3        (batch, 1024,  8,  8)
layer4        (batch, 2048,  4,  4)  ← 4x4로 마무리, 의미 있는 feature map
avgpool       (batch, 2048,  1,  1)
fc            (batch,   10)
```

1) ResNet50
- 실험 결과
	- Test Accuracy: 88.41%
	- 학습 시간 : 30:08 (10 epoch)
- 빠른 수렴을 위해 Adam optimizer를 사용했음에도 학습 시간이 오래 걸림. 
- 과적합의 가능성? 

#### 결론
- 인풋 데이터에 맞춰서 사전학습 모델 구조를 변경하여 학습한 것이 가장 성능이 좋았다.


----
### 2. 이미지 데이터셋과 사전 훈련된 VGG16 모델을 가져와 전이 학습을 수행하세요.
-----
#### 방법 1. Partial Fine Tuning
- VGG16 모델의 구조와 가중치를 가져온 후 가중치를 고정한다.
- 마지막 output layer를 수정한다.
- 수정한 레이어의 가중치만 업데이트 되게 됨.
- 실험 결과
	- Epoch 10/10|Loss: 1.5333|Val(Test) Accuracy: 0.6163|Time:0:04:53
	- Vgg_Partial_Fine Test Accuracy: 61.63%

##### 문제점
- 손실 값이 줄어들지 않았고 오히려 커졌으며 성능이 향상되지 못하였다.

#### 방법 2. Full Fine Tuning
- VGG16 모델의 구조와 가중치를 가져온 후 가중치를 고정하지 않는다.
- 마지막 output layer를 수정한다.
- 실험 결과
	- Vgg_Full Test Accuracy: 77.01%
##### 개선된 점
- 손실 값이 착실히 줄어들었고 성능이 향상되었음.

----
### 3. 동일한 데이터셋에서 ResNet과 VGG16을 각각 학습시켜 성능을 비교하세요.
---
#### Full Fine Tuning으로 선택하여 비교
- ResNet18과 VGG16을 비교
- 실험 결과
- Resnet18 Accuracy: 80.10% 
- Vgg16 Accuracy: 67.86% 
- Resnet18 has better accuracy than Vgg16

- 그래프로 비교 
<img width="1601" height="528" alt="Image" src="https://github.com/user-attachments/assets/3f47e8a7-e071-4930-bce4-829d6c97fe20" />

----
### 4. 가상 데이터셋을 생성한 뒤, GridSearch 와 RandomSearch 기법으로 하이퍼파라미터 튜닝을 진행하세요.
---
#### 데이터셋과 모델
- 가상의 데이터셋을 생성하여 Random Forest Model을 이용함.
- 강의 교재 코드를 참고하여 실험하였다.
- GridSearchCV와 RandomizedSearchCV를 이용하여 하이퍼파라미터 튜닝

```
Grid Search Best Hyperparameters: {'max_depth': 20, 'min_samples_split': 10, 'n_estimators': 100} 
Tuned Model with Grid Search - Train Accuracy: 0.96375, Test Accuracy:0.925 

Random Search Best Hyperparamters: {'max_depth': 10, 'min_samples_split': 6, 'n_estimators': 191} 
Tuned Model with Grid Search - Train Accuracy: 0.97625, Test Accuracy:0.92
```

---- 
### 5. 한국어 또는 영어 챗봇을 만드세요.
- [링크](https://github.com/100-hours-a-week/KTB4-Sian-AI/tree/main/5%EC%A3%BC%EC%B0%A8/Chatbot)
---
### 위클리 챌린지를 수행하며 알게 된 점

1) 사전 훈련 모델을 사용하는 세가지 방법
- Training from scratch : 구조만 가져오고 학습된 가중치는 가져오지 않는다.
- Full Fine Tuning : 구조와 학습된 가중치를 갖고 온 후 그 가중치를 시작점으로 삼아 가중치 업데이트
- Partial Fine Tuning : 구조와 학습된 가중치를 갖고 온 후 가중치 일부를 Freeze 시켜놓고 나머지 가중치를 학습 시킨다.

2) 선택할 때 고려할 점
- 사전 학습된 모델이 학습시 사용한 데이터와 내가 학습할 데이터의 관계를 고려해야 한다.
- 각 레이어를 통과하며 변화되는 인풋 데이터의 shape를 파악하고 그 의미를 이해해야 한다.

#### 회고
- 위클리 챌린지를 통해 사전 학습 모델의 사용법을 익힐 수 있었다.
- 사전학습모델을 가져와서 파인 튜닝하는 여러가지 방법을 실험하는 과정에서 이런 방법을 사용하면 이런 의미가 있고를 깨달을 수 있었다. 

- 이번주는 모델 튜닝 과제에만 몰입하여 실험하다보니 챗봇 과제를 여유롭게 수행하지 못하여 그 점이 아쉽다. 아무래도 익숙하지 않은 언어 모델보다는 CNN 모델이 익숙하여 이런 상황이 된 것 같다. 
- 문제를 두려워하지 않기로 했는데 맞닥뜨려보지 못한 문제도 몰입하여 푸는 자세가 필요할 것 같다.
