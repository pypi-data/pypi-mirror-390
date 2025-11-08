import pyperclip
q1="""#include <iostream>
using namespace std;
// Function to find minimum value in the array
int findMin(int arr[], int n) {
    int min = arr[0];
    for(int i = 1; i < n; i++) {
        if(arr[i] < min)
            min = arr[i];
    }
    return min;
}
// Function to find maximum value in the array
int findMax(int arr[], int n) {
    int max = arr[0];
    for(int i = 1; i < n; i++) {
        if(arr[i] > max)
            max = arr[i];
    }
    return max;
}
int main() {
    int N;
    cout<<"Enter the number of elements: ";
    cin >> N;
    int arr[N]; 
    // C++ variable-length array (OK in many compilers)
    cout << "Enter " << N << " integers:"<<endl;
    for(int i = 0; i < N; i++) {
        cin >> arr[i];
    }

    int minVal = findMin(arr, N);
    int maxVal = findMax(arr, N);
    cout << "Minimum value: " << minVal << endl;
    cout << "Maximum value: " << maxVal << endl;

    return 0;
}
"""
q2="""#include <iostream>
using namespace std;
void quickSort(int a[], int low, int high) {
    if (low < high) {
        int pivot = a[high], i = low - 1;
        for (int j = low; j < high; j++)
            if (a[j] < pivot) swap(a[++i], a[j]);
        swap(a[i + 1], a[high]);
        int pi = i + 1;
        quickSort(a, low, pi - 1);
        quickSort(a, pi + 1, high);
    }
}
void merge(int a[], int l, int m, int r) {
    int n1 = m - l + 1, n2 = r - m;
    int L[50], R[50];
    for (int i = 0; i < n1; i++) L[i] = a[l + i];
    for (int j = 0; j < n2; j++) R[j] = a[m + 1 + j];
    int i = 0, j = 0, k = l;
    while (i < n1 && j < n2) a[k++] = (L[i] <= R[j]) ? L[i++] : R[j++];
    while (i < n1) a[k++] = L[i++];
    while (j < n2) a[k++] = R[j++];
}
void mergeSort(int a[], int l, int r) {
    if (l < r) {
        int m = (l + r) / 2;
        mergeSort(a, l, m);
        mergeSort(a, m + 1, r);    
  merge(a, l, m, r);
    }
}
void display(int a[], int n) {
    cout << "Sorted Array: ";
    for (int i = 0; i < n; i++) cout << a[i] << " ";
    cout << endl;
}
int main() {
    int n, ch;
    cout << "Enter number of elements: ";
    cin >> n;
    int* arr = new int[n];
    cout << "Enter elements: ";
    for (int i = 0; i < n; i++) cin >> arr[i];
    cout << <<endl<<"Choose Sorting Method:"<<endl;
    cout << "1. Quick Sort  2. Merge Sort "<<endl<<"Enter choice: ";
    cin >> ch;
   if (ch == 1) {
        quickSort(arr, 0, n - 1);
        display(arr, n);
    } else if (ch == 2) {
        mergeSort(arr, 0, n - 1);
        display(arr, n);
    } else {
        cout << "Invalid choice."<<endl;
    }
  delete[] arr;
    return 0;
}
"""
q3="""#include <iostream>
#include <cstring>
using namespace std;
const int MAX = 100;

// Function to perform linear search
void linearSearch(char names[][50], int n, const char target[]) {
    for (int i = 0; i < n; i++) {
        if (strcmp(names[i], target) == 0) {
            cout << "Found at position " << i + 1 << endl;
            return;
        }
    }
    cout << "Name not found."<<endl;
}
// Insertion Sort (Alphabetical)
void insertionSort(char names[][50], int n) {
    for (int i = 1; i < n; i++) {
        char key[50];
        strcpy(key, names[i]);
        int j = i - 1;
        while (j >= 0 && strcmp(names[j], key) > 0) {
            strcpy(names[j + 1], names[j]);
            j--;
        }
        strcpy(names[j + 1], key);
    }
cout << "Names sorted alphabetically."<<endl;
}// Binary Search (requires sorted array)
void binarySearch(char names[][50], int n, const char target[]) {
    int left = 0, right = n - 1;
    while (left <= right) {
        int mid = (left + right) / 2;
        int cmp = strcmp(names[mid], target);
        if (cmp == 0) {
            cout << "Found at position " << mid + 1 << endl;
            return;
        } else if (cmp < 0) {
            left = mid + 1;
        } else {
            right = mid - 1;
        }
    }
    cout << "Name not found."<<endl;
}
// Display all names
void display(char names[][50], int n) {
    cout << "Student Names:"<<endl;
    for (int i = 0; i < n; i++)
        cout << i + 1 << ". " << names[i] << endl;
}

int main() {
    int n, choice;
    char names[MAX][50], searchName[50];

    cout << "Enter number of students: ";
    cin >> n;
    cin.ignore(); // Clear input buffer
    cout << "Enter student names:"<<endl;
    for (int i = 0; i < n; i++) {
        cout << "Student " << i + 1 << ": ";
        cin.getline(names[i], 50);
    }
    do {
        cout << "--- MENU ---"<<endl;
        cout << "1. Linear Search 2. Insertion Sort (A-Z) 3. Binary Search 4. Display Names 5. Exit"<<endl;
        cout << "Enter your choice: ";
        cin >> choice;
        cin.ignore(); // Clear input buffer
       
    switch (choice) {
            case 1:
                cout << "Enter name to search: ";
                cin.getline(searchName, 50);
                linearSearch(names, n, searchName);
                break;
            case 2:
                insertionSort(names, n);
                break;
            case 3:
                cout << "Enter name to search: ";
                cin.getline(searchName, 50);
                binarySearch(names, n, searchName);
                break;
            case 4:
                display(names, n);
                break;
            case 5:
                cout << "Exiting..."<<endl;
                break;
            default:
                cout << "Invalid choice!"<<endl;
        }
    } while (choice != 5);
    return 0;
}
"""
q4="""#include <iostream>
using namespace std;
class Company {
public:
    string name, location;
    int employees;
    Company* next;
    Company(string n, string l, int e) {
        name = n;
        location = l;
        employees = e;
        next = nullptr;
    }
};
class CompanyList {
    Company* head;
public:
    CompanyList() { head = nullptr; }
   void createList(int n) {
        for (int i = 0; i < n; i++) {
            string name, loc;
            int emp;
            cout << "Enter Company " << i + 1 << " Name, Location, Employees: ";
            cin >> name >> loc >> emp;
            appendCompany(name, loc, emp);
        }
    }
    void appendCompany(string name, string loc, int emp) {
        Company* newComp = new Company(name, loc, emp);
        if (!head) {
            head = newComp;
        } else {
            Company* temp = head;
            while (temp->next) temp = temp->next;
            temp->next = newComp;
        }
    }
    void addAtBeginning(string name, string loc, int emp) {
        Company* newComp = new Company(name, loc, emp);
        newComp->next = head;
        head = newComp;
    }
    void findEmployees(string cname) {
        Company* temp = head;
        while (temp) {
            if (temp->name == cname) {
                cout << "Employees in " << cname << ": " << temp->employees << endl;
                return;
            }
            temp = temp->next;
        }
        cout << "Company not found!"<<endl;
    }
   void findLocation(string cname) {
        Company* temp = head;
        while (temp) {
            if (temp->name == cname) {
                cout << "Location of " << cname << ": " << temp->location << endl;
                return;
            }
            temp = temp->next;
        }
        cout << "Company not found!"<<endl;
    }
   void display() {
        Company* temp = head;
        while (temp) {
            cout << "Name: " << temp->name << ", Location: " << temp->location << ", Employees: " << temp->employees << endl;
            temp = temp->next;
        }
    }
};

int main() {
    CompanyList clist;
    int choice, n, emp;
    string name, loc;
 do {
        cout << "1. Create List  2. Append Company  3. Add at Beginning 4. Find Employees 5. Find Location 6. Display All 0. Exit Enter choice: ";
        cin >> choice;
       switch (choice) {
            case 1:
                cout << "Enter number of companies: ";
                cin >> n;
                clist.createList(n);
                break;
            case 2:
                cout << "Enter Name, Location, Employees: ";
                cin >> name >> loc >> emp;
                clist.appendCompany(name, loc, emp);
                break;
            case 3:
                cout << "Enter Name, Location, Employees: ";
                cin >> name >> loc >> emp;
                clist.addAtBeginning(name, loc, emp);
                break;
            case 4:
                cout << "Enter Company Name: ";
                cin >> name;
                clist.findEmployees(name);
                break;
            case 5:
                cout << "Enter Company Name: ";
                cin >> name;
                clist.findLocation(name);
                break;
            case 6:
                clist.display();
                break;
        }
    } while (choice != 0);
    return 0;
}
"""
q5="""#include <iostream>
#include <cstring>
using namespace std;

// Node for doubly linked list
class Doctor {
public:
    char name[50], specialization[50], phone[15];
    Doctor *prev, *next;
    Doctor(const char* n, const char* s, const char* p) {
        strcpy(name, n);
        strcpy(specialization, s);
        strcpy(phone, p);
        prev = next = NULL;
    }
};

// List class
class DoctorList {
    Doctor* head;
public:
    DoctorList() { head = NULL; }

    // Append a new doctor
    void appendDoctor() {
        char name[50], spec[50], phone[15];
        cout << endl<<"Enter Doctor Name: ";
        cin.ignore(); cin.getline(name, 50);
        cout << "Enter Specialization: ";
        cin.getline(spec, 50);
        cout << "Enter Phone Number: ";
        cin.getline(phone, 15);

        Doctor* d = new Doctor(name, spec, phone);

        if (!head) head = d;
        else {
            Doctor* temp = head;
            while (temp->next) temp = temp->next;
            temp->next = d;
            d->prev = temp;
        }
    }

    // Display all doctors of a given specialization
    void listBySpecialization(const char* spec) {
        bool found = false;
        Doctor* temp = head;
        cout << "Doctors with specialization '" << spec << "':";
        while (temp) {
            if (strcmp(temp->specialization, spec) == 0) {
                cout << "Name: " << temp->name << ", Phone: " << temp->phone << endl;
                found = true;
            }
            temp = temp->next;
        }
        if (!found)
            cout << "No doctors found with this specialization.";
    }

    // Reverse the list
    void reverseList() {
        Doctor* temp = head;
        Doctor* prevNode = NULL;

        while (temp) {
            prevNode = temp->prev;
            temp->prev = temp->next;
            temp->next = prevNode;
            temp = temp->prev;
        }

        if (prevNode)
            head = prevNode->prev;

        cout << "List reversed."<<endl;
    }

    // Display the full list
    void displayAll() {
        Doctor* temp = head;
        cout << endl<<"Doctor List:"<<endl;
        while (temp) {
            cout << "Name: " << temp->name
                 << ", Specialization: " << temp->specialization
                 << ", Phone: " << temp->phone << endl;
            temp = temp->next;
        }
    }
};

// Main function
int main() {
    DoctorList list;
    int choice;
    char spec[50];
    do {
        cout << "--- MENU ---"<<endl;
        cout << "1. Append Doctor 2. List by Specialization 3. Reverse List 4. Display All 5. Exit"<<endl;
        cout << "Enter your choice: ";
        cin >> choice;

        switch (choice) {
            case 1:
                list.appendDoctor();
                break;
            case 2:
                cout << "Enter specialization to search: ";
                cin.ignore(); cin.getline(spec, 50);
                list.listBySpecialization(spec);
                break;
            case 3:
                list.reverseList();
                break;
            case 4:
                list.displayAll();
                break;
            case 5:
                cout << "Exiting..."<<endl;
                break;
            default:
                cout << "Invalid choice."<<endl;
        }
    } while (choice != 5);
    return 0;
}
"""
def DSAQ1():
    pyperclip.copy(q1)
def DSAQ2():
    pyperclip.copy(q2)
def DSAQ3():
    pyperclip.copy(q3)
def DSAQ4():
    pyperclip.copy(q2)
def DSAQ5():
    pyperclip.copy(q2)
#DSAQ2()