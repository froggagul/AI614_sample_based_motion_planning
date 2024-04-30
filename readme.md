Reconsidering Random Tree search

1. uniform random sample all the configurations from the configuration space.
2. iterate through all the configurations. make a one edge at each iteration. edge should be made between q_i and (q_1, ..., q_{i-1})

위 알고리즘은 RRT, naive RRT를 포함한다. RRT는 q_0~q_{i-1} 중에서 가장 가까운 노드를 찾고, naive RRT는 q_0~q_{i-1} 중에서 랜덤하게 노드를 선택한다.

해당 알고리즘을 사용하면 어떤 configuration q에 대해서도 epsilon 거리 이내에 있는 path를 찾을 수 있음을 증명할 수 있다.

우선 어떤 node는 configuration q에 대해서 epsilon 거리 이내에 있을 확률이 1임을 증명해보자.

Lemma 1. 그대로

그러면 path가 존재하는가?
알고리즘의 2번 줄에서, q_i는 무조건 q_0~q_{i-1} 중에서 랜덤한 노드를 선택한다. 그렇기 때문에, q_i에서 q_0로 가는 path가 무조건 존재한다.

Lemma 2.

q_0 -> q'_0이 존재
q_0 -> q'_1이 존재. 따라서, q'_0 -> q'_1이 존재

이렇게 반복하면, q'_0 -> q'_i가 존재한다.

끝!
