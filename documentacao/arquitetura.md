<img width="3241" height="717" alt="image" src="https://github.com/user-attachments/assets/b6ca9562-c319-4fd7-a33e-53cd1e6cce3c" />
Esse primeiro diagrama está mais limpo para deixar vísivel mais elementos, o diagrama mais próximo do real é o segundo.

 ## Arquitetura
  A arquitetura desse projeto  acaba sendo um Big Ball of Mud , você pode ver o screening.py de services em flask_backend como exemplo, além de ter o mesmo nome de outra classe(screening.py de routes), ela aponta para qualquer lugar no backend, demonstrado no segundo plantuml diagram, esse diagrama abaixo ainda está incompleto, mas já da para ver por quê vira esse Big Ball of Mud

 ##Justificativa
  Esse projeto mistura varios aspectos no backend, em si cada um deles tem sua funcionalidade e propósitos certinhos, o problema só chega na hora de comunicação entre os outros módulos, apesar disso é possível identificar elementos necessários para mudanças, só aumenta a dificuldade dessa tarefa, corrigindo essas interações a arquitetura se tornaria um MVC Web pelo detalhe dessa divisão do frontend simples e backend grande executado em cima do banco de dados que os scrapers puxam.

<img width="3102" height="717" alt="image" src="https://github.com/user-attachments/assets/b4c1e3e9-2c43-4eac-87dc-74cb3931177e" />
