# Ethical considerations for application design in NLP

>“[...] we might be puzzled or amused when receiving an email addressing us with the wrong gender, or congratulating us to our retirement on our 30th birthday. In practice, though, relying on models that produce false positives may lead to bias confirmation and overgeneralization. Would we accept the same error rates if the system was used to predict sexual orientation or religious views, rather than age or gender? Given the right training data, this is just a matter of changing the target variable.” (Hovy and Spruit, 2016)

## Description:
When we design applications for our robot, we need to consider the stakeholders and the potential societal impact. The overarching goal of the projects in this course is to design and implement modules for detecting friend and kinship relations from multimodal signals and store the results in the brain. In this sub-project we will use the example of binary gender classification to explore ethical problems that can arise when designing NLP technologies. Students will be provided with relevant readings and we will discuss these during the group meetings. Subsequently we will design a module that takes our findings from the readings and discussions into account, makes use of the robots communicative capabilities and moves away from binary classification to a more inclusive approach. 

## Possible approaches
There are several ways how to design this more inclusive approach, we will discuss two main ones. We can either approach it as a **problem of the training data** and try to work with datasets that include non-binary as a class or we **create a communicative module** to handle this. This would mean that we keep the gender variable empty until it has been confirmed by a user. This can happen in different ways, we can make Leolani explicitly ask for clarification or we can wait until pronouns are mentioned during conversation. We also have to decide on how Leolani should refer to people until she is certain of their pronouns, especially in the context of kinship terms.

## Readings
1. [The Social Impact of Natural Language Processing](https://www.aclweb.org/anthology/P16-2096/)
	-  [Video of the ACL talk](http://techtalks.tv/talks/the-social-impact-of-natural-language-processing/63253/)
3. [Fairness and Abstraction in Sociotechnical Systems](http://sorelle.friedler.net/papers/sts_fat2019.pdf)
4. [Ethical by Design: Ethics Best Practices for Natural Language Processing](http://www.ethicsinnlp.org/workshop/pdf/EthNLP02.pdf)
5. [Gender as a Variable in Natural-Language Processing: Ethical Considerations](https://scholarship.law.tamu.edu/cgi/viewcontent.cgi?referer=&httpsredir=1&article=1831&context=facscholar)
6. [Gender Classification and Bias Mitigation in Facial Images](https://dl.acm.org/doi/pdf/10.1145/3394231.3397900) ([arxiv](https://arxiv.org/pdf/2007.06141.pdf))
	- [Reply by Os Keyes of the University of Washington](https://ironholds.org/debiasing/)
