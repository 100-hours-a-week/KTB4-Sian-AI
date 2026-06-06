## 4주차 위클리 챌린지
### 1. 가상 데이터 셋을 생성한 뒤, 학습·검증·테스트 데이터셋으로 분할해 보세요.

#### 데이터셋
넘파이 랜덤으로 1000x32x32x3 shape의 가상 데이터 셋 생성 후, train_test_split 메서드로 데이터셋 분할.
#### 데이터셋 분할
우선, train set과 temp set으로 데이터를 60:40으로 분할 후
temp set을 다시 50:50으로 test set 과 valid set 으로 분할한다.

따라서 학습 데이터 셋 600개, 검증 데이터 셋 200개, 테스트 데이터 셋 200개로 분할하게 된다.

### 2. 가상 데이터셋을 생성하고, K-최근접이웃(K-NN) 알고리즘으로 학습·예측을 수행해보세요.

#### 데이터셋
1000x20 shape의 랜덤 값으로 이루어진 가상 데이터 셋을 학습 데이터로 사용하고, 0~9로 이루어진 랜덤 정수 값 1000개 모음을 학습 데이터 레이블로 사용한다. 마찬가지로 200개의 가상 학습 데이터와 200개의 레이블을 생성해 테스트 데이터 셋으로 사용한다.
#### K-NN 모델 생성 및 학습
sklearn의 메서드를 이용해 K-NN 모델을 생성하고 학습한다.
```
# K-NN 모델 생성
k = 5
knn_model = KNeighborsClassifier(n_neighbors=k)

#모델 학습
knn_model.fit(X_train, y_train)
```
#### 모델 평가 및 예측
score 메소드를 이용해 정확도를 측정하고 predict 메소드로 샘플 데이터 (테스트 데이터셋의 첫번째 데이터)의 예측값을 알아낸다.

### 3. 동일한 이진 분류 가상 데이터셋을 생성하고, Perceptron, SVM, Random Forest, Naive Bayes 네 가지 알고리즘으로 학습해보세요.
#### 데이터셋
1000x20 shape의 랜덤 값으로 이루어진 가상 데이터 셋을 학습 데이터로 사용하고, 0~1로 이루어진(이진 분류) 랜덤 정수 값 1000개를 학습 데이터 레이블로 사용한다. 마찬가지로 200개의 가상 학습 데이터와 200개의 레이블을 생성해 테스트 데이터 셋으로 사용한다.

#### 모델 생성 및 학습
sklearn의 메서드를 이용해 Perceptron, SVM, RandomForest, Naive Bayes 모델을 생성하고 학습한다.
```
from sklearn.linear_model import Perceptron
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB

# Perceptron
pn_model = Perceptron(random_state=42)

# SVM
svm_model = SVC(kernel='linear')

# RandomForest
rf_model1 = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model2 = RandomForestClassifier(n_estimators=100,max_depth=10,random_state=42)

# Naive Bayes
nb_model = GaussianNB()
```

```
# 모델 학습
pn_model.fit(X_train, y_train)
svm_model.fit(X_train, y_train)
rf_model1.fit(X_train, y_train)
rf_model2.fit(X_train, y_train)
nb_model.fit(X_train, y_train)
```
#### 모델 평가 및 예측
score 메소드를 이용해 정확도를 측정하고 predict 메소드로 샘플 데이터 (테스트 데이터셋의 첫번째 데이터)의 예측값을 알아낸다.

### 4. 가상 데이터셋을 준비하고, 증강(Data Augmentation) 기법을 적용했을 때와 적용하지 않았을 때 모델 성능을 비교하세요.
#### 데이터셋
데이터 증강 기법은 주로 이미지 데이터에 사용되기 때문에 **CIFAR-10**을 데이터셋으로 선택하였다.

`torchvision.datasets.CIFAR10` 을 이용해 데이터 셋을 다운로드 받고 가져온다.

#### 데이터 증강 적용
torchvision.transforms로 적용하고자 하는 데이터 증강 기법을 적용한다.
##### 기본적인 transforms : 데이터 증강할 때도 똑같이 적용
`transforms.ToTensor()`
픽셀 값을 255로 나누어 0.0~1.0 사이의 float32 값으로 바꿔준다.
또한 차원 순서를 파이토치 텐서에 맞게 변경해준다 : HWC -> CHW

`transforms.Normalize(mean=(0.5,0.5,0.5), std=(0.5,0.5,0.5))`
픽셀 값을 표준화해준다. = 데이터 정규화
R,G,B 각 채널의 평균과 표준편차를 설정해주어 정규화 해준다.

##### 데이터 증강 transforms
`transforms.RandomHorizontalFlip(p=0.5)`
랜덤한 확률(p)로 이미지를 대칭으로 뒤집어준다.  

`transforms.RandomRotation(degrees = 15)`
랜덤하게 이미지를 회전시켜준다. 

`transforms.ColorJitter(brightness=0.2, contrast=0.2)`
랜덤하게 밝기나 명도 등을 바꿔준다.

#### 실험 결과
num epochs : 10
model : Simple CNN 

**학습 결과**
- 데이터 증강 없이 : 정확도 73.57%
- 데이터 증강 적용 : 정확도 79.29%
- 데이터 증강을 적용한 결과 정확도가 증가한 것을 확인할 수 있다
- 데이터 증강이 학습 성능에 도움을 주었다.

### 5. 활성화 함수를 직접 정의하고, 활성화 함수를 적용한 출력을 계산하고, 결과를 그래프로 시각화하세요.
#### 활성화 함수 정의
```
def sigmoid(x):
	return 1 / (1+np.exp(-x))

def tanh(x):
	return np.tanh(x)

def relu(x):
	return np.maximum(0, x)
```

#### 활성화 함수 적용 결과
인풋 : (-10~10)

**그래프 시각화**
![[Pasted image 20260606143017.png]]

### 6.비선형 데이터셋을 생성하고, MLP(다층 퍼셉트론) 모델을 설계하고 학습시켜 분류를 수행하세요.
#### 데이터셋
`sklearn.datasets` 이용하여 Iris 데이터 셋을 사용함.
분류 클래스 개수(num classes) : 3개
input dimension : 4

Iris data : 150 x 4
train data : 120 x 4
test data : 30 x 4

#### MLP 설계
```
class MLP(nn.Module):
	def __init__(self, input_dim, num_classes):
		super(MLP, self).__init__()
		self.fc1 = nn.Linear(input_dim, 64)
		self.fc2 = nn.Linear(64,64)
		self.fc3 = nn.Linear(64, num_classes)

	def forward(self, x):
		x = torch.relu(self.fc1(x))
		x = torch.relu(self.fc2(x))	
		x = self.fc3(x)

		return x
```


### 7. CNN(Convolutional Neural Network)을 직접 구성하여 이미지 분류를 수행하세요.
#### 데이터셋
4번 문제에서 사용한 CIFAR-10을 사용하여 CNN을 학습 시킴.

분류 클래스 개수 : 10
CIFAR-10 shape : 32 x 32 x 3

#### CNN 모델 생성
SimpleCNN과 VGG16 구조를 참고하여 설계
```
class CNN(nn.Module):
	def __init__(self):
		super(SimpleCNN, self).__init__()
		self.conv1 = nn.Conv2d(3, 32, kernel_size=3, padding=1)
		self.conv2 = nn.Conv2d(32, 64, kernel_size=3, padding=1)
		self.conv3 = nn.Conv2d(64, 128, kernel_size=3, padding=1)
		self.pool = nn.MaxPool2d(kernel_size=2, stride=2) # output size 1/2
		self.flatten = nn.Flatten()
		self.fc1 = nn.Linear(128 *4*4, 512)
		self.fc2 = nn.Linear(512, num_classes) # output layer
	
	def forward(self, x):
		x = self.pool(torch.relu(self.conv1(x))) # 16x16x32
		x = self.pool(torch.relu(self.conv2(x))) # 8x8x64
		x = self.pool(torch.relu(self.conv3(x))) # 4x4x128
		x = self.flatten(x)
		x = torch.relu(self.fc1(x))
		x = self.fc2(x) # output 이므로 activation 적용하지 않음
		return x
```

#### 손실함수, 옵티마이저
손실함수 : Cross Entropy Loss
옵티마이저 : Adam 사용

#### 학습 결과
num epochs : 10
정확도 : 74.68%


## 위클리 챌린지 회고
### 고민한 점
- 이미지 데이터를 불러와서 학습에 사용하는 순간부터 학습 속도가 매우 떨어져서 GPU 사용 설정이 필요해 강의 교재를 참고하여 코랩에서 GPU 사용하는 방법을 적용시켰다.
- epoch 수가 10번으로 상대적으로 매우 적은 편인데 

### 개선 방안
- CNN 모델 구조를 개선하거나 에포크 수, Loss, Optimizer 등을 바꿔가며 성능을 비교해보기.
- 코랩 환경에서는 한계점이 많음
- 아나콘다 환경에 익숙해져 있어서 다른 환경에서 학습 시키는 것에 대해 알아야한다.



