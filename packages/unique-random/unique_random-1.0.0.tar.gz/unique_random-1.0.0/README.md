**\# unique\_random**

* Generate **unique random numbers** efficiently, with optional persistence across runs using bitmap storage.    
* Designed for large-scale data pipelines, simulations, and systems where duplicate random values are not acceptable.

**\# 📦 Features**

* Generates unique random numbers in a given range    
* Optional persistence \- remembers previously generated numbers between runs  
* Configurable behavior when numbers are exhausted (\`error\`, \`reset\`, \`repeat\`)    
* Efficient bitmap-based storage (ideal for large ranges, up to billions)    
* Command-line interface (\`unirand\`) for quick use    
* Well-tested and lightweight \- no external dependencies  

**\# 🧑‍💻Installation**

\#\#\# From GitHub (development branch)

| pip install git+https://github.com/sairohithpasupuleti/unique\_random.git@develop |
| :---- |

## **🧰 Basic Usage**

| from unique\_random import UniqueRandom \# Create a generator that remembers state ur \= UniqueRandom(1, 100, persistent=True) for \_ in range(5):     print(ur.randint()) ur.close() |
| :---- |

| Output: 27 84 3 99 41 |
| :---- |

## **💻 Command-Line Interface (CLI)**

After installation, you can use the `unirand` command directly in your terminal.

### **Generate numbers**

| unirand \--generate 5 \--start 1 \--end 100 |
| :---- |

### **View current stats**

| unirand \--stats \--start 1 \--end 100 |
| :---- |

### **Reset state**

| unirand \--reset \--start 1 \--end 100 |
| :---- |

Example output:

| Generating 5 unique numbers: 27 53 98 84 2 |
| :---- |

## **🚀 Options**

| Option | Description | Default |
| :---- | :---- | :---- |
| \--generate N | Number of values to generate | \- |
| \--start N | Start of range | Required |
| \--end N | End of range | Required |
| \--persistent | Store bitmap state for future runs | False |
| \--on-exhaust | Behavior when all numbers are used (`error`, `reset`, `repeat`) | error |
| \--reset | Reset bitmap state file | \- |
| \--stats | Show usage stats | \- |

## **💡 Example: Persistent Mode**

The persistent mode keeps track of already generated numbers using a binary bitmap file.

| unirand \--generate 10 \--start 1 \--end 1000000 \--persistent |
| :---- |

If you run it again later, it will continue generating unused numbers from the same range, without repetition.

State files are stored in:

\~/.unique\_random/state\_\<start\>\_\<end\>.bin

---

## **🧑‍💻Development Setup**

| git clone https://github.com/sairohithpasupuleti/unique\_random.git cd unique\_random python3 \-m venv .venv source .venv/bin/activate pip install \-e . pytest \-q |
| :---- |

## **🔒 License**

This project is licensed under the **MIT License**.  
 See the [LICENSE](https://github.com/sairohithpasupuleti/unique_random/blob/develop/LICENSE) file for full details.

---

## **👤 Author**

**Sai Rohith Pasupuleti**  
 📧 sairohithpasupuleti@gmail.com  
 🌐 [GitHub Repository](https://github.com/sairohithpasupuleti/unique_random)

## **🧭 Roadmap**

- Add C-backed bitmap for improved speed (v1.1)  
- Optional multi-threaded random generation  
- Built-in benchmarking mode  
- Integration tests with 1B+ values

## **🤝 Contributing**

Contributions are welcome\!🧑‍💻  
If you'd like to improve this package:

* Fork the repository  
* Create a new branch (`feature/...`)  
* Submit a pull request

## **⭐ Support**

If you find this project useful, please consider starring it on GitHub.  
Your support motivates continued development.

