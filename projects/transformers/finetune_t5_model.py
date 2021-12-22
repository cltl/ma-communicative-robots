# Code inspired from: https://github.com/MathewAlexander/T5_nlg
# import packages
import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration
from transformers.optimization import Adafactor
from IPython.display import HTML, display
import pandas as pd

# we will be using T5-large with the data set having all the triples merged together.

# load your data set
train_df = pd.read_csv('merged_all_triples.csv', index_col=[0])
train_df = train_df.iloc[:35000, :]
train_df = train_df.sample(frac=1) #Return a random sample of the df
# defining batch size, number of batches and epochs
# epoch are  forward pass and backward pass of all the training sets
# batch size is  number of training examples in one forward/backward pass.
batch_size = 8
num_of_batches = len(train_df) / batch_size
num_of_epochs = 1

num_of_batches = int(num_of_batches)
# starting tokenizer for our model (T5)
tokenizer = T5Tokenizer.from_pretrained('t5-large')
model = T5ForConditionalGeneration.from_pretrained('t5-large', return_dict=True)

# initializing gpu
if torch.cuda.is_available():
    dev = torch.device("cuda:0")
    print("Running on the GPU")
else:
    dev = torch.device("cpu")
    print("Running on the CPU")

# moving the model to device(GPU/CPU)
model.to(dev)

# here we have optimizer in which we will define our model's parameters such as, learning rate, eps etc
# optimizer provides a fixed  weight decay, that can be used to fine-tuned models.
optimizer = Adafactor(
    model.parameters(),
    lr=1e-3,
    eps=(1e-30, 1e-3),
    clip_threshold=1.0,
    decay_rate=-0.8,
    beta1=None,
    weight_decay=0.0,
    relative_step=False,
    scale_parameter=False,
    warmup_init=False
)


def progress(loss, value, max=100):
    return HTML(""" Batch loss :{loss}
        <progress
            value='{value}'
            max='{max}',
            style='width: 100%'
        >
            {value}
        </progress>
    """.format(loss=loss,value=value, max=max))

num_of_epochs = 3

"""## Training the model"""
# Sets the module in training mode
# we will be training with 3 epochs.

model.train()

loss_per_10_steps=[]
for epoch in range(1,num_of_epochs+1):
    print('Running epoch: {}'.format(epoch))
  
    running_loss=0

    out = display(progress(1, num_of_batches+1), display_id=True)
    for i in range(num_of_batches):
        inputbatch = []  # for input text
        labelbatch = []  # for target text
        new_df = train_df[i*batch_size:i*batch_size+batch_size] # new dataset from the old one
        for indx, row in new_df.iterrows():
            # defining input text and target text as input and labels
            input = 'WebNLG: ' + row['input_text'] + '</s>'
            labels = row['target_text'] + '</s>'
            inputbatch.append(input)
            labelbatch.append(labels)

        inputbatch = tokenizer.batch_encode_plus(inputbatch,padding=True,max_length=400,return_tensors='pt')["input_ids"]
        labelbatch = tokenizer.batch_encode_plus(labelbatch,padding=True,max_length=400,return_tensors="pt") ["input_ids"]
        inputbatch = inputbatch.to(dev)
        labelbatch = labelbatch.to(dev)

        # clear out the gradients of all Variables
        optimizer.zero_grad()

        # Forward propagation with output, loss and loss number
        outputs = model(input_ids=inputbatch, labels=labelbatch)
        loss = outputs.loss
        loss_num = loss.item()
        logits = outputs.logits
        running_loss += loss_num
        if i%10 == 0:
            loss_per_10_steps.append(loss_num)
        try:
            out.update(progress(loss_num,i, num_of_batches+1))
        except AttributeError:
            continue

        # calculating the gradients
        loss.backward()

        # updating the parameters using optimizer
        optimizer.step()
    
        running_loss=running_loss/int(num_of_batches)
        print('Epoch: {} , Running loss: {}'.format(epoch,running_loss))


# save the trained model using torch.save.
torch.save(model.state_dict(),'pytoch_model.bin')

# download the config file
# !wget https://s3.amazonaws.com/models.huggingface.co/bert/t5-base-config.json
# again defining tokenizer and model, this time model is the one we trained. (saved model)
tokenizer = T5Tokenizer.from_pretrained('t5-base')
model = T5ForConditionalGeneration.from_pretrained('path_to_trained_model',
                                                return_dict=True)

# generate function for generating output using our trained model and test data set
def generate(text,model,tokenizer):
   model.eval()  # evaluating the model
   input_ids = tokenizer.encode("WebNLG:{} </s>".format(text), 
                               return_tensors="pt")  
   outputs = model.generate(input_ids) # generating sentences

   return tokenizer.decode(outputs[0])


# test our model
model.eval()
input_ids = tokenizer.encode("WebNLG: sidharth | hometown | Delhi && sidharth | play |  football </s>", return_tensors="pt")  # Batch size 1
input_ids=input_ids.to(dev)
outputs = model.generate(input_ids)
tokenizer.decode(outputs[0])

model.eval()
input_ids = tokenizer.encode("DART: Dwayne Johnson | nickName  | The Rock && Dwayne Johnson | actor | movie </s>", return_tensors="pt")  # Batch size 1
input_ids = input_ids.to(dev)
outputs = model.generate(input_ids)
tokenizer.decode(outputs[0])

model.eval()
input_ids = tokenizer.encode("DART: Dwayne Johnson | actor | Red Notice && Netflix | creator | Red Notice </s>", return_tensors="pt")  # Batch size 1
input_ids = input_ids.to(dev)
outputs = model.generate(input_ids)
tokenizer.decode(outputs[0])

