import torch
from torch import nn
from torchvision import datasets, transforms
from torch.utils.data.dataset import random_split
from VGG.VGG import VGG11, VGG13, VGG16, VGG19
from ResNet.Resnet import ResNet18, ResNet34, ResNet50
import matplotlib.pyplot as plt
import typer

app = typer.Typer()

USE_CUDA = torch.cuda.is_available()
device = torch.device("cuda:2" if USE_CUDA else "cpu")

def train(model, optimizer, criterion, train_loader):
    model.train()
    train_correct = 0.0
    total_train = 0.0
    train_loss = 0.0
    for x, y in train_loader:
        x = x.to(device)
        y = y.to(device)

        optimizer.zero_grad()
        outputs = model(x)
        loss = criterion(outputs, y)
        loss.backward()
        optimizer.step()

        _, preds = torch.max(outputs, 1)
        train_correct += torch.sum(preds == y.data)
        total_train += y.size(0)
        train_loss += loss.item()

    epoch_loss = train_loss / total_train
    epoch_acc = train_correct.float() * 100 / total_train

    return epoch_loss, epoch_acc

def evaluate(model, criterion, test_loader):
    model.eval()
    val_correct = 0.0
    val_loss = 0.0
    total_test = 0.0
    with torch.no_grad():
        for x, y in test_loader:
            x = x.to(device)
            y = y.to(device)
            outputs = model(x)
            loss = criterion(outputs, y)

            _, preds = torch.max(outputs, 1)
            val_correct += torch.sum(preds == y.data)
            total_test += y.size(0)
            val_loss += loss.item()

    val_epoch_loss = val_loss / total_test
    val_epoch_acc = val_correct.float() * 100 / total_test

    return val_epoch_loss, val_epoch_acc

@app.command("cifar10")
def cifar_10(aa:str):
    transformer = transforms.Compose(
        [transforms.ToTensor(), transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))]
    )

    batch_size = 128
    epochs = 50
    learning_rate = 0.01

    train_dataset = datasets.CIFAR10(
        root="./data", train=True, download=True, transform=transformer
    )
    test_dataset = datasets.CIFAR10(
        root="./data", train=False, download=True, transform=transformer
    )

    train_dataset, _ = random_split(train_dataset, [10000,40000])

    train_loader = torch.utils.data.DataLoader(
        dataset=train_dataset, batch_size=batch_size, shuffle=True
    )
    test_loader = torch.utils.data.DataLoader(
        dataset=test_dataset, batch_size=batch_size, shuffle=False
    )

    if aa == "VGG19":
        model = VGG19()
    elif aa == "ResNet18":
        model = ResNet18()
    elif aa == "ResNet34":
        model = ResNet34()
    elif aa == "ResNet50":
        model = ResNet50()


    model = model.to(device)
    criterion = nn.CrossEntropyLoss().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)

    train_acc_list = []
    val_acc_list = []
    for epoch in range(epochs):
        train_loss, train_acc = train(model, optimizer, criterion, train_loader)
        val_loss, val_acc = evaluate(model, criterion, test_loader)
        train_acc_list.append(train_acc)
        val_acc_list.append(val_acc)

        print("[Epoch :  {}]".format(epoch + 1))
        print("train loss : {:.5f}, acc : {:.5f}".format(train_loss, train_acc))
        print("val loss : {:.5f}, acc : {:.5f}".format(val_loss, val_acc))

    plt.plot(train_acc_list, val_acc_list)
    plt.show()