import pyperclip
bubble="""void bubbleSort(int arr[], int n) {
    for (int i = 0; i < n - 1; i++)
        for (int j = 0; j < n - i - 1; j++)
            if (arr[j] > arr[j + 1])
                swap(arr[j], arr[j + 1]);
}
"""
selection="""void selectionSort(int arr[], int n) {
    for (int i = 0; i < n - 1; i++) {
        int minIndex = i;
        for (int j = i + 1; j < n; j++)
            if (arr[j] < arr[minIndex])
                minIndex = j;
        swap(arr[i], arr[minIndex]);
    }
}
"""
insertion="""void insertionSort(int arr[], int n) {
    for (int i = 1; i < n; i++) {
        int key = arr[i];
        int j = i - 1;
        while (j >= 0 && arr[j] > key) {
            arr[j + 1] = arr[j];
            j--;
        }
        arr[j + 1] = key;
    }
}
"""
merge="""void merge(int arr[], int l, int m, int r) {
    int n1 = m - l + 1, n2 = r - m;
    int L[n1], R[n2];
    for (int i = 0; i < n1; i++) L[i] = arr[l + i];
    for (int j = 0; j < n2; j++) R[j] = arr[m + 1 + j];
    int i = 0, j = 0, k = l;
    while (i < n1 && j < n2) arr[k++] = (L[i] <= R[j]) ? L[i++] : R[j++];
    while (i < n1) arr[k++] = L[i++];
    while (j < n2) arr[k++] = R[j++];
}

void mergeSort(int arr[], int l, int r) {
    if (l < r) {
        int m = l + (r - l) / 2;
        mergeSort(arr, l, m);
        mergeSort(arr, m + 1, r);
        merge(arr, l, m, r);
    }
}
"""
quick="""int partition(int arr[], int low, int high) {
    int pivot = arr[high];
    int i = low - 1;
    for (int j = low; j < high; j++) {
        if (arr[j] < pivot) {
            i++;
            swap(arr[i], arr[j]);
        }
    }
    swap(arr[i + 1], arr[high]);
    return i + 1;
}
void quickSort(int arr[], int low, int high) {
    if (low < high) {
        int pi = partition(arr, low, high);
        quickSort(arr, low, pi - 1);
        quickSort(arr, pi + 1, high);
    }
}
"""
singlelinkedliststr="""#include <iostream>
using namespace std;

class SinglyLinkedList {
private:
    struct Node {
        int data;
        Node* next;
        Node(int val) : data(val), next(nullptr) {}
    };
    
    Node* head;

public:
    SinglyLinkedList() : head(nullptr) {}
    
    // Create/Insert operations
    void insertAtBeginning(int val) {
        Node* newNode = new Node(val);
        newNode->next = head;
        head = newNode;
    }
    
    void insertAtEnd(int val) {
        Node* newNode = new Node(val);
        if (!head) {
            head = newNode;
            return;
        }
        
        Node* temp = head;
        while (temp->next) {
            temp = temp->next;
        }
        temp->next = newNode;
    }
    
    void insertAtPosition(int val, int pos) {
        if (pos < 1) {
            cout << "Invalid position!" << endl;
            return;
        }
        
        if (pos == 1) {
            insertAtBeginning(val);
            return;
        }
        
        Node* newNode = new Node(val);
        Node* temp = head;
        
        for (int i = 1; i < pos - 1 && temp; i++) {
            temp = temp->next;
        }
        
        if (!temp) {
            cout << "Position out of range!" << endl;
            delete newNode;
            return;
        }
        
        newNode->next = temp->next;
        temp->next = newNode;
    }
    
    // Delete operations
    void deleteFromBeginning() {
        if (!head) {
            cout << "List is empty!" << endl;
            return;
        }
        
        Node* temp = head;
        head = head->next;
        delete temp;
    }
    
    void deleteFromEnd() {
        if (!head) {
            cout << "List is empty!" << endl;
            return;
        }
        
        if (!head->next) {
            delete head;
            head = nullptr;
            return;
        }
        
        Node* temp = head;
        while (temp->next->next) {
            temp = temp->next;
        }
        
        delete temp->next;
        temp->next = nullptr;
    }
    
    void deleteFromPosition(int pos) {
        if (!head || pos < 1) {
            cout << "Invalid position or empty list!" << endl;
            return;
        }
        
        if (pos == 1) {
            deleteFromBeginning();
            return;
        }
        
        Node* temp = head;
        for (int i = 1; i < pos - 1 && temp; i++) {
            temp = temp->next;
        }
        
        if (!temp || !temp->next) {
            cout << "Position out of range!" << endl;
            return;
        }
        
        Node* nodeToDelete = temp->next;
        temp->next = temp->next->next;
        delete nodeToDelete;
    }
    
    // Search operation
    bool search(int val) {
        Node* temp = head;
        int position = 1;
        
        while (temp) {
            if (temp->data == val) {
                cout << "Value " << val << " found at position " << position << endl;
                return true;
            }
            temp = temp->next;
            position++;
        }
        
        cout << "Value " << val << " not found in the list" << endl;
        return false;
    }
    
    // Display operation
    void display() {
        if (!head) {
            cout << "List is empty!" << endl;
            return;
        }
        
        Node* temp = head;
        cout << "Singly Linked List: ";
        while (temp) {
            cout << temp->data << " -> ";
            temp = temp->next;
        }
        cout << "NULL" << endl;
    }
    
    ~SinglyLinkedList() {
        while (head) {
            Node* temp = head;
            head = head->next;
            delete temp;
        }
    }
};
"""
doublelinkedliststr="""class DoublyLinkedList {
private:
    struct Node {
        int data;
        Node* prev;
        Node* next;
        Node(int val) : data(val), prev(nullptr), next(nullptr) {}
    };
    
    Node* head;
    Node* tail;

public:
    DoublyLinkedList() : head(nullptr), tail(nullptr) {}
    
    // Insert operations
    void insertAtBeginning(int val) {
        Node* newNode = new Node(val);
        
        if (!head) {
            head = tail = newNode;
        } else {
            newNode->next = head;
            head->prev = newNode;
            head = newNode;
        }
    }
    
    void insertAtEnd(int val) {
        Node* newNode = new Node(val);
        
        if (!tail) {
            head = tail = newNode;
        } else {
            tail->next = newNode;
            newNode->prev = tail;
            tail = newNode;
        }
    }
    
    void insertAtPosition(int val, int pos) {
        if (pos < 1) {
            cout << "Invalid position!" << endl;
            return;
        }
        
        if (pos == 1) {
            insertAtBeginning(val);
            return;
        }
        
        Node* temp = head;
        for (int i = 1; i < pos - 1 && temp; i++) {
            temp = temp->next;
        }
        
        if (!temp) {
            cout << "Position out of range!" << endl;
            return;
        }
        
        Node* newNode = new Node(val);
        newNode->next = temp->next;
        newNode->prev = temp;
        
        if (temp->next) {
            temp->next->prev = newNode;
        } else {
            tail = newNode;
        }
        
        temp->next = newNode;
    }
    
    // Delete operations
    void deleteFromBeginning() {
        if (!head) {
            cout << "List is empty!" << endl;
            return;
        }
        
        Node* temp = head;
        head = head->next;
        
        if (head) {
            head->prev = nullptr;
        } else {
            tail = nullptr;
        }
        
        delete temp;
    }
    
    void deleteFromEnd() {
        if (!tail) {
            cout << "List is empty!" << endl;
            return;
        }
        
        Node* temp = tail;
        tail = tail->prev;
        
        if (tail) {
            tail->next = nullptr;
        } else {
            head = nullptr;
        }
        
        delete temp;
    }
    
    void deleteFromPosition(int pos) {
        if (!head || pos < 1) {
            cout << "Invalid position or empty list!" << endl;
            return;
        }
        
        if (pos == 1) {
            deleteFromBeginning();
            return;
        }
        
        Node* temp = head;
        for (int i = 1; i < pos && temp; i++) {
            temp = temp->next;
        }
        
        if (!temp) {
            cout << "Position out of range!" << endl;
            return;
        }
        
        if (temp->prev) {
            temp->prev->next = temp->next;
        }
        
        if (temp->next) {
            temp->next->prev = temp->prev;
        } else {
            tail = temp->prev;
        }
        
        delete temp;
    }
    
    // Search operation
    bool search(int val) {
        Node* temp = head;
        int position = 1;
        
        while (temp) {
            if (temp->data == val) {
                cout << "Value " << val << " found at position " << position << endl;
                return true;
            }
            temp = temp->next;
            position++;
        }
        
        cout << "Value " << val << " not found in the list" << endl;
        return false;
    }
    
    // Display operations
    void displayForward() {
        if (!head) {
            cout << "List is empty!" << endl;
            return;
        }
        
        Node* temp = head;
        cout << "Doubly Linked List (Forward): ";
        while (temp) {
            cout << temp->data << " <-> ";
            temp = temp->next;
        }
        cout << "NULL" << endl;
    }
    
    void displayBackward() {
        if (!tail) {
            cout << "List is empty!" << endl;
            return;
        }
        
        Node* temp = tail;
        cout << "Doubly Linked List (Backward): ";
        while (temp) {
            cout << temp->data << " <-> ";
            temp = temp->prev;
        }
        cout << "NULL" << endl;
    }
    
    ~DoublyLinkedList() {
        while (head) {
            Node* temp = head;
            head = head->next;
            delete temp;
        }
    }
};"""
circularlinkedliststr="""class CircularLinkedList {
private:
    struct Node {
        int data;
        Node* next;
        Node(int val) : data(val), next(nullptr) {}
    };
    
    Node* last; // Points to the last node

public:
    CircularLinkedList() : last(nullptr) {}
    
    // Insert operations
    void insertAtBeginning(int val) {
        Node* newNode = new Node(val);
        
        if (!last) {
            last = newNode;
            last->next = last; // Point to itself
        } else {
            newNode->next = last->next;
            last->next = newNode;
        }
    }
    
    void insertAtEnd(int val) {
        Node* newNode = new Node(val);
        
        if (!last) {
            last = newNode;
            last->next = last;
        } else {
            newNode->next = last->next;
            last->next = newNode;
            last = newNode;
        }
    }
    
    void insertAtPosition(int val, int pos) {
        if (pos < 1) {
            cout << "Invalid position!" << endl;
            return;
        }
        
        if (pos == 1 || !last) {
            insertAtBeginning(val);
            return;
        }
        
        Node* temp = last->next; // Start from first node
        for (int i = 1; i < pos - 1 && temp != last; i++) {
            temp = temp->next;
        }
        
        // If position is beyond the list length, insert at end
        if (temp == last) {
            insertAtEnd(val);
            return;
        }
        
        Node* newNode = new Node(val);
        newNode->next = temp->next;
        temp->next = newNode;
    }
    
    // Delete operations
    void deleteFromBeginning() {
        if (!last) {
            cout << "List is empty!" << endl;
            return;
        }
        
        Node* temp = last->next; // First node
        
        if (last->next == last) { // Only one node
            delete last;
            last = nullptr;
        } else {
            last->next = temp->next;
            delete temp;
        }
    }
    
    void deleteFromEnd() {
        if (!last) {
            cout << "List is empty!" << endl;
            return;
        }
        
        if (last->next == last) { // Only one node
            delete last;
            last = nullptr;
            return;
        }
        
        Node* temp = last->next; // Start from first node
        while (temp->next != last) {
            temp = temp->next;
        }
        
        temp->next = last->next;
        delete last;
        last = temp;
    }
    
    void deleteFromPosition(int pos) {
        if (!last || pos < 1) {
            cout << "Invalid position or empty list!" << endl;
            return;
        }
        
        if (pos == 1) {
            deleteFromBeginning();
            return;
        }
        
        Node* temp = last->next; // First node
        Node* prev = nullptr;
        
        for (int i = 1; i < pos && temp != last; i++) {
            prev = temp;
            temp = temp->next;
        }
        
        // If position is beyond the list length
        if (temp == last && pos > 1) {
            if (pos == getLength()) {
                deleteFromEnd();
            } else {
                cout << "Position out of range!" << endl;
            }
            return;
        }
        
        prev->next = temp->next;
        
        // If we're deleting the last node, update last pointer
        if (temp == last) {
            last = prev;
        }
        
        delete temp;
    }
    
    // Search operation
    bool search(int val) {
        if (!last) {
            cout << "List is empty!" << endl;
            return false;
        }
        
        Node* temp = last->next; // Start from first node
        int position = 1;
        
        do {
            if (temp->data == val) {
                cout << "Value " << val << " found at position " << position << endl;
                return true;
            }
            temp = temp->next;
            position++;
        } while (temp != last->next);
        
        cout << "Value " << val << " not found in the list" << endl;
        return false;
    }
    
    // Display operation
    void display() {
        if (!last) {
            cout << "List is empty!" << endl;
            return;
        }
        
        Node* temp = last->next; // Start from first node
        cout << "Circular Linked List: ";
        
        do {
            cout << temp->data << " -> ";
            temp = temp->next;
        } while (temp != last->next);
        
        cout << "(back to first)" << endl;
    }
    
    // Helper function to get length
    int getLength() {
        if (!last) return 0;
        
        int count = 0;
        Node* temp = last->next;
        
        do {
            count++;
            temp = temp->next;
        } while (temp != last->next);
        
        return count;
    }
    
    ~CircularLinkedList() {
        if (!last) return;
        
        Node* current = last->next;
        Node* nextNode;
        
        while (current != last) {
            nextNode = current->next;
            delete current;
            current = nextNode;
        }
        delete last;
    }
};
"""
converterstr="""class ExpressionConverter {
private:
    // Helper function to check if character is operator
    static bool isOperator(char c) {
        return (c == '+' || c == '-' || c == '*' || c == '/' || c == '^');
    }

    // Helper function to get precedence of operators
    static int getPrecedence(char op) {
        if (op == '^') return 3;
        if (op == '*' || op == '/') return 2;
        if (op == '+' || op == '-') return 1;
        return 0;
    }

public:
    // Infix to Postfix conversion
    static string infixToPostfix(const string& infix) {
        string postfix = "";
        ArrayStack opStack(infix.length());
        
        for (char c : infix) {
            // If operand, add to output
            if (isalnum(c)) {
                postfix += c;
            }
            // If '(', push to stack
            else if (c == '(') {
                opStack.push(c);
            }
            // If ')', pop until '('
            else if (c == ')') {
                while (!opStack.isEmpty() && opStack.peek() != '(') {
                    postfix += opStack.pop();
                }
                opStack.pop(); // Remove '('
            }
            // If operator
            else if (isOperator(c)) {
                while (!opStack.isEmpty() && getPrecedence(opStack.peek()) >= getPrecedence(c)) {
                    postfix += opStack.pop();
                }
                opStack.push(c);
            }
        }
        
        // Pop all remaining operators
        while (!opStack.isEmpty()) {
            postfix += opStack.pop();
        }
        
        return postfix;
    }
    // Infix to Prefix conversion
    static string infixToPrefix(const string& infix) {
        string reversedInfix = infix;
        reverse(reversedInfix.begin(), reversedInfix.end());
        
        // Replace '(' with ')' and vice versa
        for (char& c : reversedInfix) {
            if (c == '(') c = ')';
            else if (c == ')') c = '(';
        }
        
        string postfix = infixToPostfix(reversedInfix);
        reverse(postfix.begin(), postfix.end());
        return postfix;
    }
};
"""
evaluatestr="""class ExpressionEvaluator {
private:
    // Helper function to perform operation
    static int applyOperation(int a, int b, char op) {
        switch (op) {
            case '+': return a + b;
            case '-': return a - b;
            case '*': return a * b;
            case '/': 
                if (b == 0) throw runtime_error("Division by zero!");
                return a / b;
            case '^': return pow(a, b);
            default: throw runtime_error("Invalid operator!");
        }
    }

public:
    // Evaluate Postfix expression
    static int evaluatePostfix(const string& postfix) {
        ArrayStack stack(postfix.length());
        
        for (char c : postfix) {
            // If operand, push to stack
            if (isdigit(c)) {
                stack.push(c - '0');
            }
            // If operator, pop two operands and apply operation
            else if (ExpressionConverter::isOperator(c)) {
                int b = stack.pop();
                int a = stack.pop();
                int result = applyOperation(a, b, c);
                stack.push(result);
            }
        }
        return stack.pop();
    }

    // Evaluate Prefix expression
    static int evaluatePrefix(const string& prefix) {
        ArrayStack stack(prefix.length());
        
        // Traverse from right to left for prefix evaluation
        for (int i = prefix.length() - 1; i >= 0; i--) {
            char c = prefix[i];
            
            // If operand, push to stack
            if (isdigit(c)) {
                stack.push(c - '0');
            }
            // If operator, pop two operands and apply operation
            else if (ExpressionConverter::isOperator(c)) {
                int a = stack.pop();
                int b = stack.pop();
                int result = applyOperation(a, b, c);
                stack.push(result);
            }
        }
        return stack.pop();
    }
};
"""
arraystackstr="""#include <iostream>
#include <stdexcept>
#include <vector>
#include <algorithm>
using namespace std;

// Stack ADT using Array (Sequential Organization)
class ArrayStack {
private:
    int* arr;
    int capacity;
    int top;

public:
    ArrayStack(int size = 1000) {
        capacity = size;
        arr = new int[capacity];
        top = -1;
    }

    ~ArrayStack() {
        delete[] arr;
    }

    // Push operation
    void push(int value) {
        if (isFull()) {
            throw overflow_error("Stack Overflow!");
        }
        arr[++top] = value;
    }

    // Pop operation
    int pop() {
        if (isEmpty()) {
            throw underflow_error("Stack Underflow!");
        }
        return arr[top--];
    }

    // Peek operation
    int peek() {
        if (isEmpty()) {
            throw underflow_error("Stack is empty!");
        }
        return arr[top];
    }

    // Check if stack is empty
    bool isEmpty() {
        return top == -1;
    }

    // Check if stack is full
    bool isFull() {
        return top == capacity - 1;
    }

    // Get size of stack
    int size() {
        return top + 1;
    }

    // Display stack
    void display() {
        if (isEmpty()) {
            cout << "Stack is empty!" << endl;
            return;
        }
        cout << "Stack (top to bottom): ";
        for (int i = top; i >= 0; i--) {
            cout << arr[i] << " ";
        }
        cout << endl;
    }
};"""
arrayqueuestr="""#include <iostream>
#include <stdexcept>

template<typename T, int MAX_SIZE = 10>
class FixedArrayQueue {
private:
    T queue[MAX_SIZE];
    int front;
    int rear;
    int currentSize;

public:
    // Constructor
    FixedArrayQueue() : front(0), rear(-1), currentSize(0) {}

    // Add element to the rear of the queue
    void enqueue(const T& item) {
        if (isFull()) {
            throw std::overflow_error("Queue is full");
        }
        
        rear = (rear + 1) % MAX_SIZE;
        queue[rear] = item;
        currentSize++;
    }

    // Remove and return element from the front of the queue
    T dequeue() {
        if (isEmpty()) {
            throw std::underflow_error("Cannot dequeue from empty queue");
        }
        
        T item = queue[front];
        front = (front + 1) % MAX_SIZE;
        currentSize--;
        return item;
    }

    // Return element from the front without removing it
    T peek() const {
        if (isEmpty()) {
            throw std::underflow_error("Cannot peek empty queue");
        }
        return queue[front];
    }

    // Check if queue is empty
    bool isEmpty() const {
        return currentSize == 0;
    }

    // Check if queue is full
    bool isFull() const {
        return currentSize == MAX_SIZE;
    }

    // Get current size of queue
    int size() const {
        return currentSize;
    }

    // Get maximum capacity of queue
    constexpr int capacity() const {
        return MAX_SIZE;
    }

    // Display queue contents
    void display() const {
        if (isEmpty()) {
            std::cout << "Queue is empty" << std::endl;
            return;
        }
        
        std::cout << "Queue (front to rear): ";
        for (int i = 0; i < currentSize; i++) {
            std::cout << queue[(front + i) % MAX_SIZE] << " ";
        }
        std::cout << std::endl;
    }

    // Clear all elements from queue
    void clear() {
        front = 0;
        rear = -1;
        currentSize = 0;
    }

    // Get available space
    int available() const {
        return MAX_SIZE - currentSize;
    }
};
"""
def quicksort():
    pyperclip.copy(quick)
def mergesort():
    pyperclip.copy(merge)
def bubblesort():
    pyperclip.copy(bubble)
def selectionsort():
    pyperclip.copy(selection)
def insertionsort():
    pyperclip.copy(insertion)
def singlelinkedlist():
    pyperclip.copy(singlelinkedliststr)
def doublelinkedlist():
    pyperclip.copy(doublelinkedliststr)
def circularlinkedlist():
    pyperclip.copy(circularlinkedliststr)
def converter():
    pyperclip.copy(converterstr)
def evaluate():
    pyperclip.copy(evaluatestr)
def arraystack():
    pyperclip.copy(arraystackstr)
def arrayqueue():
    pyperclip.copy(arrayqueuestr)

def show():
    pyperclip.copy("""
    arraystack
    arrayqueue
    converter
    circularlinkedlist
    mergesort
    quicksort
    selectionsort
    insertionsort
    doublelinkedlist
    singlelinkedlist
    doublelinkedlist
    evaluate""")
if __name__=="__main__":
    arraystack()
