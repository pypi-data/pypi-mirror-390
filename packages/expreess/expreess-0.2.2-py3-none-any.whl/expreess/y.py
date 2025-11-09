codes: 


Has1

{ Build interactive UI blocks using hooks, refs, usestate(), useeffect() in React front end 

App.js 

import React, { useState, useEffect, useRef } from "react";

function App() {
  const [count, setCount] = useState(0);            
  const [text, setText] = useState("");           
  const inputRef = useRef(null);                   

  
  useEffect(() => {
    console.log("Count updated:", count);
  }, [count]);

  
  const focusInput = () => {
    inputRef.current.focus();
  };

  return (
    <div style={{ textAlign: "center", marginTop: "40px" }}>
      <h2>React Hooks Demo</h2>

      
      <p>Counter Value: {count}</p>
      <button onClick={() => setCount(count + 1)}>Increment</button>

      <br /><br />

      
      <input
        ref={inputRef}
        type="text"
        placeholder="Type something..."
        value={text}
        onChange={(e) => setText(e.target.value)}
      />
      <button onClick={focusInput}>Focus Input</button>

      <p>You typed: {text}</p>
    </div>
  );
}

export default App;

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



Has2
{ Use functional components for reusable UI elements like headers, footers, and navigation bars.}

App.js 
 
import React from "react"; 
import Header from "./Header"; 
import Navbar from "./Navbar"; 
import Footer from "./Footer"; 
 
function App() { 
  return ( 
    <div> 
      <Header /> 
      <Navbar /> 
      <h2>Welcome to My Website</h2> 
      <p>This is a simple example using functional components in React.</p> 
      <Footer /> 
    </div> 
  ); 
} 
 
export default App; 
 
Header.js  
 
function Header() { 
  return <h1>My Website</h1>; 
} 
 
export default Header; 
 
Navbar.js 
 
function Navbar() { 
  return ( 
    <nav> 
      <a href="#home">Home</a> |  
      <a href="#about">About</a> |  
      <a href="#contact">Contact</a> 
    </nav> 
  ); 
} 
 
export default Navbar; 
 
Footer.js 
 
function Footer() { 
  return ( 
    <footer> 
      <p>&copy; 2025 All Rights Reserved</p> 
    </footer> 
  ); 
} 
 
export default Footer;

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



Has3

{ Implement a form to add new student details (Name, Roll No, Department)and Display the entered student records dynamically using a list component.}

import React, { useState } from "react"; 
import './App.css'; 
function StudentForm() { 
  const [students, setStudents] = useState([]); 
  const [form, setForm] = useState({ name: "", rollNo: "", department: "" }); 
 
  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value }); 
 
  const handleSubmit = (e) => { 
    e.preventDefault(); 
    setStudents([...students, form]); 
    setForm({ name: "", rollNo: "", department: "" }); 
  }; 
 
  return ( 
    <div> 
      <form onSubmit={handleSubmit}> 
 
        <input name="name" 
         placeholder="Name" 
         value={form.name} 
         onChange={handleChange} required /> 
        <input name="rollNo" 
         placeholder="Roll No" 
         value={form.rollNo} 
         onChange={handleChange} required /> 
        <input name="department" 
         placeholder="Department" 
         value={form.department} 
         onChange={handleChange} required /> 
 
        <button type="submit">Add</button> 
      </form> 
      <ul> 
        {students.map((s, i) => <li key={i}> 
          {s.name} - {s.rollNo} - {s.department}</li>)} 
      </ul> 
    </div> 
  ); 
} 
 
export default StudentForm;

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


Has4 
 { Include navigation between Home, Register, and Registered Users pages using React Router.}
commond to run before runing this code = npm i react-router-dom

App.js
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import Home from "./pages/Home";
import Register from "./pages/Register";
import Users from "./pages/Users";

export default function App() {
  return (
    <BrowserRouter>
      <nav style={{ display: "flex", gap: 15, padding: 10 }}>
        <Link to="/">Home</Link>
        <Link to="/register">Register</Link>
        <Link to="/users">Users</Link>
      </nav>

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/register" element={<Register />} />
        <Route path="/users" element={<Users />} />
      </Routes>
    </BrowserRouter>
  );
}

Home.js
export default function Home() {
  return <h2>Home Page</h2>;
}	

Register.js
export default function Register() {
  return <h2>Register Page</h2>;
}

User.js
export default function Users() {
  return <h2>Registered Users Page</h2>;
}

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


Has5
{ Design a functional component that uses useState() to manage a list of tasks.}

import React, { useState } from "react";

function TaskList() {
  const [tasks, setTasks] = useState([]);
  const [input, setInput] = useState("");

  const addTask = () => {
    if (input.trim() !== "") {
      setTasks([...tasks, input]);
      setInput("");
    }
  };

  return (
    <div>
      <h3>Task List</h3>

      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Enter task"
      />

      <button onClick={addTask}>Add Task</button>

      <ul>
        {tasks.map((task, index) => (
          <li key={index}>{task}</li>
        ))}
      </ul>
    </div>
  );
}

export default TaskList;

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Has6

{ Use useRef() to automatically focus the input box when the page loads. }

import React, { useState, useRef, useEffect } from "react";

function SimpleInput() {
  const [text, setText] = useState("");
  const inputRef = useRef(null);

  useEffect(() => {
    inputRef.current.focus(); // auto focus when page loads
  }, []);

  return (
    <div>
      <h3>Auto Focus Input Example</h3>

      <input
        ref={inputRef}
        type="text"
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder="Type something..."
      />

      <p>You typed: {text}</p>
    </div>
  );
}

export default SimpleInput;

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



Has7	

{Use useEffect() to update the clock every second.}

import React, { useState, useEffect } from "react";

function Clock() {
  const [time, setTime] = useState(new Date().toLocaleTimeString());

  useEffect(() => {
    const timer = setInterval(() => {
      setTime(new Date().toLocaleTimeString());
    }, 1000);

    return () => clearInterval(timer); // cleanup
  }, []);

  return (
    <div>
      <h3>Current Time</h3>
      <p>{time}</p>
    </div>
  );
}

export default Clock;

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


Has8

{ Create a json file to store data and fetch using list component }

save this json file " data.json "
[
  { "id": 1, "name": "Rahul", "course": "React" },
  { "id": 2, "name": "Sneha", "course": "Node.js" },
  { "id": 3, "name": "Amit", "course": "MongoDB" }
]

app.js
import React, { useState, useEffect } from "react";
import data from "./data.json";   // import json file

function App() {
  const [students, setStudents] = useState([]);

  useEffect(() => {
    setStudents(data); // load json data
  }, []);

  return (
    <div>
      <h3>Student List</h3>
      <ul>
        {students.map((s) => (
          <li key={s.id}>
            {s.name} - {s.course}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


Has9
{ Create a parent component (App.js) to hold employee data, Pass data (Employee Name, ID, Department) to a child component (Employee.js) using props and Display at least three employee cards dynamically using the same reusable component. }

app.js 
import React from "react";
import Employee from "./Employee";

function App() {
  const employees = [
    { id: 101, name: "Rahul Sharma", dept: "HR" },
    { id: 102, name: "Sneha Patil", dept: "Finance" },
    { id: 103, name: "Amit Verma", dept: "IT" }
  ];

  return (
    <div>
      <h2>Employee List</h2>

      {employees.map(emp => (
        <Employee 
          key={emp.id}
          id={emp.id}
          name={emp.name}
          dept={emp.dept}
        />
      ))}
    </div>
  );
}

export default App;

Employee.js
import React from "react";

function Employee(props) {
  return (
    <div style={{ border: "1px solid black", padding: "10px", margin: "10px" }}>
      <p><b>ID:</b> {props.id}</p>
      <p><b>Name:</b> {props.name}</p>
      <p><b>Department:</b> {props.dept}</p>
    </div>
  );
}

export default Employee;

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


Has10
{ Perform the following operations using synchronous 
a.	Create and write data to a file named data.txt.
b.	Append additional content to the same file.
c.	Read the content of the file and display it in the console.
d.	Delete the file after reading. }


const fs = require("fs");


fs.writeFileSync("data.txt", "Hello, this is first line.\n");
console.log("File created and data written.");


fs.appendFileSync("data.txt", "This is appended text.\n");
console.log("Data appended.");


const content = fs.readFileSync("data.txt", "utf8");
console.log("File Content:\n", content);


fs.unlinkSync("data.txt");
console.log("File deleted.");

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


Has11
{ Perform the following operations using asynchronous 
a.	Create and write data to a file named data.txt.
b.	Append additional content to the same file.
c.	Read the content of the file and display it in the console.
d.	Delete the file after reading. }


const fs = require("fs");

// Step 1: Create and write to file
fs.writeFile("data.txt", "Hello! This is the initial file content.", () => {
  console.log("✅ Step 1: File created and data written.");

  // Step 2: Append more content
  fs.appendFile("data.txt", "\nThis is the appended content.", () => {
    console.log("✅ Step 2: Additional data appended.");

    // Step 3: Read file content
    fs.readFile("data.txt", "utf8", ( _ , data ) => {
      console.log("✅ Step 3: File content:\n");
      console.log(data);

      // Step 4: Delete the file
      fs.unlink("data.txt", () => {
        console.log("\n✅ Step 4: File deleted.");
      });
    });
  });
});

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


Has12 
{ Create a Node.js script Use Readable and Writable Streams to perform following operation 
a.	Read data from a large file (input.txt) 
b.	Write the streamed data into another file (output.txt) }

* create first input.txt file 

const fs = require("fs");

const readStream = fs.createReadStream("input.txt");

const writeStream = fs.createWriteStream("output.txt");

readStream.pipe(writeStream);

readStream.on("data", (chunk) => { 
  console.log("📦 Reading chunk:", chunk.length, "bytes");
});

readStream.on("end", () => { 
  console.log("✅ Streaming completed. Data copied to output.txt");
});

writeStream.on("finish", () => {
  console.log("✅ Write stream closed.");
});


------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


Has13
{ Create a Node.js file named bufferExample.js.Perform the following tasks:
a.	Create a Buffer from a string 
b.	Display the buffer content in raw, string, and JSON format.
c.	Create an empty buffer of size 10 and fill it with a value.
d.	Modify buffer content using indexing.
e.	Concatenate two buffers and display the result. }

// 1. Create a Buffer from a string
const buf1 = Buffer.from("Hello Node");

// Display buffer in raw format
console.log("🔹 Raw Buffer:", buf1);

// Display buffer as string
console.log("🔹 Buffer as String:", buf1.toString());

// Display buffer as JSON
console.log("🔹 Buffer as JSON:", buf1.toJSON());

// 2. Create an empty buffer of size 10 and fill it
const buf2 = Buffer.alloc(10);
buf2.fill(65); // filling with ASCII value 65 = 'A'
console.log("🔹 Filled Buffer:", buf2);

// 3. Modify buffer content using indexing
buf2[0] = 90; // ASCII 90 = 'Z'
console.log("🔹 After modifying index 0:", buf2);

// 4. Concatenate two buffers
const buf3 = Buffer.from(" World");
const result = Buffer.concat([buf1, buf3]);
console.log("🔹 Concatenated Buffer:", result.toString());

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


Has14
{ MongoDB CRUD operations. Build an inventory management database for a small electronics store. insert a new product with fields like name, category, price, stock, and created At into the products collection.Delete the product with created At date on or before 2024.Use InsertOne and InsertMany. Use find method to search Mobile phones from products. }

✅ MongoDB Shell Version (Easiest for Exams)
1️⃣ Insert One Product
db.products.insertOne({
  name: "Laptop",
  category: "Electronics",
  price: 55000,
  stock: 10,
  createdAt: new Date("2025-01-10")
});

2️⃣ Insert Many Products
db.products.insertMany([
  {
    name: "Mobile Phone",
    category: "Mobile",
    price: 15000,
    stock: 30,
    createdAt: new Date("2024-12-15")
  },
  {
    name: "Headphones",
    category: "Audio",
    price: 2000,
    stock: 50,
    createdAt: new Date("2023-11-20")
  },
  {
    name: "Smart Watch",
    category: "Wearable",
    price: 4500,
    stock: 20,
    createdAt: new Date("2024-05-03")
  }
]);

3️⃣ Find all Mobile Phones
db.products.find({ category: "Mobile" });


OR (if name contains "Mobile")

db.products.find({ name: "Name" });

4️⃣ Delete products where createdAt ≤ 2024
db.products.deleteMany({
  createdAt: { $lte: new Date("2024-12-31") }
});

📌 What this covers
Requirement	Done?
InsertOne	✅
InsertMany	✅
Find method	✅ (search Mobile phones)
Delete with date filter	✅ (createdAt ≤ 2024)
Fields required	✅ (name, category, price, stock, createdAt)
✅ If you want the same thing in Node.js (Express + MongoDB), here is the smallest code: run this commond to download mongodb  
" npm install mongodb "

const { MongoClient } = require("mongodb");

async function run() {
  const client = await MongoClient.connect("mongodb://127.0.0.1:27017");
  const db = client.db("store");
  const products = db.collection("products");

  // Insert One
  await products.insertOne({
    name: "Laptop",
    category: "Electronics",
    price: 55000,
    stock: 10,
    createdAt: new Date("2025-01-10")
  });

  // Insert Many
  await products.insertMany([
    { name: "Mobile Phone", category: "Mobile", price: 15000, stock: 30, createdAt: new Date("2024-12-15") },
    { name: "Headphones", category: "Audio", price: 2000, stock: 50, createdAt: new Date("2023-11-20") },
    { name: "Smart Watch", category: "Wearable", price: 4500, stock: 20, createdAt: new Date("2024-05-03") }
  ]);

  // Find Mobile phones
  console.log(await products.find({ category: "Mobile" }).toArray());

  // Delete products created in or before 2024
  await products.deleteMany({ createdAt: { $lte: new Date("2024-12-31") } });

  client.close();
}
run();

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

Has15
{ You are tasked with designing and implementing a simple backend system using MongoDB to manage data for a fictional Bookstore. The system should be capable of performing basic CRUD operations on the collection of books. Create: Insert a new book into the database. Each book should have the following fields:title (String),author (String),isbn (String, unique),published Year (Number),genre (String),price (Number)
Read: Retrieve a list of all books, Retrieve a single book by its isbn,
           Update:Update the details (e.g., price or genre) of a book using its isbn.
           Delete:Remove a book from the collection using its isbn. }



📌 Database & Collection
use bookstore;       // create/use database
db.createCollection("books");

✅ 1️⃣ CREATE – Insert One Book
db.books.insertOne({
  title: "The Alchemist",
  author: "Paulo Coelho",
  isbn: "9780061122415",
  publishedYear: 1988,
  genre: "Fiction",
  price: 299
});

Insert Many (optional)
db.books.insertMany([
  {
    title: "Atomic Habits",
    author: "James Clear",
    isbn: "9780735211292",
    publishedYear: 2018,
    genre: "Self-help",
    price: 450
  },
  {
    title: "Rich Dad Poor Dad",
    author: "Robert Kiyosaki",
    isbn: "9781612680194",
    publishedYear: 1997,
    genre: "Finance",
    price: 350
  }
]);

✅ 2️⃣ READ – Retrieve All Books
db.books.find();

Retrieve Book by ISBN
db.books.findOne({ isbn: "9780061122415" });

✅ 3️⃣ UPDATE – Update Book Details (price or genre) by ISBN
db.books.updateOne(
  { isbn: "9780061122415" },       // search condition
  { $set: { price: 350, genre: "Motivational" } } // updated values
);

✅ 4️⃣ DELETE – Remove Book Using ISBN
db.books.deleteOne({ isbn: "9780061122415" });




Viva:


Has1 — Hooks + refs + useState + useEffect
Line-by-line
import React, { useState, useEffect, useRef } from "react";


– Imports React and three hooks.

function App() {


– Defines a functional component.

  const [count, setCount] = useState(0);


– Declares state count with initial value 0. setCount updates it.

  const [text, setText] = useState("");


– Declares state text bound to the input.

  const inputRef = useRef(null);


– Creates a ref object { current: null } that will later hold the input DOM node.

  useEffect(() => {
    console.log("Count updated:", count);
  }, [count]);


– Runs after render whenever count changes; logs the latest count.

  const focusInput = () => {
    inputRef.current.focus();
  };


– Imperatively focuses the input using the DOM node stored in the ref.

  return (
    <div style={{ textAlign: "center", marginTop: "40px" }}>
      <h2>React Hooks Demo</h2>


– Container and title.

      <p>Counter Value: {count}</p>
      <button onClick={() => setCount(count + 1)}>Increment</button>


– Shows current count; clicking increments state → triggers re-render.

      <br /><br />


– Visual spacing.

      <input
        ref={inputRef}
        type="text"
        placeholder="Type something..."
        value={text}
        onChange={(e) => setText(e.target.value)}
      />


– Controlled input: value comes from text; onChange updates text. ref attaches DOM node to inputRef.current.

      <button onClick={focusInput}>Focus Input</button>
      <p>You typed: {text}</p>


– Button calls focus; paragraph echoes typed text.

    </div>
  );
}
export default App;


– Ends component and exports.

Theory (viva)

useState stores component state; updating it re-renders the component.

Controlled components: inputs’ value is driven by state; onChange updates state.

useRef holds a mutable value across renders (commonly DOM nodes); changing .current doesn’t re-render.

useEffect runs after the DOM is updated; dependency array [count] means run only when count changes.

Imperative vs Declarative: most React code is declarative; refs allow occasional imperative DOM actions like focus.

Has2 — Reusable functional components
Line-by-line (App.js)
import React from "react";
import Header from "./Header";
import Navbar from "./Navbar";
import Footer from "./Footer";


– Bring in React and three children.

function App() {
  return (
    <div>
      <Header />
      <Navbar />
      <h2>Welcome to My Website</h2>
      <p>This is a simple example using functional components in React.</p>
      <Footer />
    </div>
  );
}
export default App;


– Composes the page by rendering components in order.

Header.js
function Header() { return <h1>My Website</h1>; }
export default Header;


– Stateless component returns a heading.

Navbar.js
function Navbar() {
  return (
    <nav>
      <a href="#home">Home</a> |  
      <a href="#about">About</a> |  
      <a href="#contact">Contact</a>
    </nav>
  );
}
export default Navbar;


– Simple navigation with anchors (hash links).

Footer.js
function Footer() {
  return (
    <footer>
      <p>&copy; 2025 All Rights Reserved</p>
    </footer>
  );
}
export default Footer;


– Stateless footer markup.

Theory (viva)

Component composition: big UIs = small reusable components.

Functional components: simple functions returning JSX; cheap and easy; use hooks for state/effects.

Prefer Link from React Router for SPA navigation (anchors cause full reload).

Separation of concerns improves readability, reuse, testing.

Has3 — Student form + dynamic list
Line-by-line
import React, { useState } from "react";
import './App.css';
function StudentForm() {


– Imports and starts component.

  const [students, setStudents] = useState([]);


– Array of student objects for rendering.

  const [form, setForm] = useState({ name: "", rollNo: "", department: "" });


– Single object holding all input fields.

  const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });


– Updates one field using computed property name; spreads the rest.

  const handleSubmit = (e) => {
    e.preventDefault();
    setStudents([...students, form]);
    setForm({ name: "", rollNo: "", department: "" });
  };


– Prevents reload, appends new record immutably, clears the form.

  return (
    <div>
      <form onSubmit={handleSubmit}>
        <input name="name" placeholder="Name" value={form.name} onChange={handleChange} required />
        <input name="rollNo" placeholder="Roll No" value={form.rollNo} onChange={handleChange} required />
        <input name="department" placeholder="Department" value={form.department} onChange={handleChange} required />
        <button type="submit">Add</button>
      </form>
      <ul>
        {students.map((s, i) => <li key={i}>{s.name} - {s.rollNo} - {s.department}</li>)}
      </ul>
    </div>
  );
}
export default StudentForm;


– Controlled inputs, submit button, list rendering with map.

Theory (viva)

Controlled inputs keep source of truth in React; easier validation and resetting.

Immutable updates ([...] spread) let React detect changes.

List keys: stable keys help reconciliation; for real data prefer an ID (not index).

Form handling: onSubmit + preventDefault() avoids page refresh.

Has4 — React Router (Home / Register / Users)
Line-by-line
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import Home from "./pages/Home";
import Register from "./pages/Register";
import Users from "./pages/Users";


– Import router components and pages.

export default function App() {
  return (
    <BrowserRouter>
      <nav style={{ display: "flex", gap: 15, padding: 10 }}>
        <Link to="/">Home</Link>
        <Link to="/register">Register</Link>
        <Link to="/users">Users</Link>
      </nav>


– Enables history API routing and provides SPA links.

      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/register" element={<Register />} />
        <Route path="/users" element={<Users />} />
      </Routes>
    </BrowserRouter>
  );
}


– Maps URL paths to components.

Pages:

// Home.js
export default function Home(){ return <h2>Home Page</h2>; }
// Register.js
export default function Register(){ return <h2>Register Page</h2>; }
// Users.js
export default function Users(){ return <h2>Registered Users Page</h2>; }

Theory (viva)

SPA routing swaps components on URL change without reloading.

BrowserRouter uses the History API; Link prevents full reloads.

Routes picks the best-matching Route.

Use useParams for /users/:id; useNavigate for programmatic navigation.

Has5 — Task list with useState
Line-by-line
import React, { useState } from "react";

function TaskList() {
  const [tasks, setTasks] = useState([]);
  const [input, setInput] = useState("");


– Two pieces of state: tasks array + input text.

  const addTask = () => {
    if (input.trim() !== "") {
      setTasks([...tasks, input]);
      setInput("");
    }
  };


– Validates, immutably appends, clears input.

  return (
    <div>
      <h3>Task List</h3>
      <input value={input} onChange={(e) => setInput(e.target.value)} placeholder="Enter task" />
      <button onClick={addTask}>Add Task</button>
      <ul>{tasks.map((task, index) => (<li key={index}>{task}</li>))}</ul>
    </div>
  );
}
export default TaskList;


– Controlled input, add button, list render with keys.

Theory (viva)

State drives UI: when state changes, React re-renders.

Immutability: use [...tasks, x] not tasks.push(x).

List keys: use stable IDs in real apps to avoid reconciliation bugs.

Has6 — useRef to auto-focus on mount
Line-by-line
import React, { useState, useRef, useEffect } from "react";
function SimpleInput() {
  const [text, setText] = useState("");
  const inputRef = useRef(null);


– State for text; ref for DOM input.

  useEffect(() => {
    inputRef.current.focus(); // auto focus when page loads
  }, []);


– Runs once after first render; focuses input.

  return (
    <div>
      <h3>Auto Focus Input Example</h3>
      <input ref={inputRef} value={text} onChange={(e) => setText(e.target.value)} placeholder="Type something..." />
      <p>You typed: {text}</p>
    </div>
  );
}
export default SimpleInput;


– Controlled input and echo.

Theory (viva)

Empty dependency array [] ≈ componentDidMount; effect runs once.

Refs enable imperative DOM actions in a declarative framework.

No re-render on ref change: changing .current is side-channel storage.

Has7 — Live clock with interval
Line-by-line
import React, { useState, useEffect } from "react";
function Clock() {
  const [time, setTime] = useState(new Date().toLocaleTimeString());


– Initializes time to current time string.

  useEffect(() => {
    const timer = setInterval(() => {
      setTime(new Date().toLocaleTimeString());
    }, 1000);
    return () => clearInterval(timer); // cleanup
  }, []);


– Sets 1-second interval once; cleanup stops it on unmount.

  return (
    <div>
      <h3>Current Time</h3>
      <p>{time}</p>
    </div>
  );
}
export default Clock;


– Displays live time.

Theory (viva)

Effects for side-effects like timers.

Cleanup function prevents memory leaks and duplicated intervals.

State updates trigger re-render and refresh the view.

Has8 — Import JSON and render list
Line-by-line
import React, { useState, useEffect } from "react";
import data from "./data.json";


– Imports static JSON at build time.

function App() {
  const [students, setStudents] = useState([]);
  useEffect(() => { setStudents(data); }, []);


– On mount, copy JSON to state (so you can modify later if needed).

  return (
    <div>
      <h3>Student List</h3>
      <ul>
        {students.map((s) => (
          <li key={s.id}>{s.name} - {s.course}</li>
        ))}
      </ul>
    </div>
  );
}
export default App;


– Renders list with keys.

data.json

[
  { "id": 1, "name": "Rahul", "course": "React" },
  { "id": 2, "name": "Sneha", "course": "Node.js" },
  { "id": 3, "name": "Amit", "course": "MongoDB" }
]

Theory (viva)

Static import (bundled) vs fetch (runtime). Import is great for fixed demo data.

Keys must be unique and stable.

State copy allows later operations (add/remove) and reactivity.

Has9 — Parent → Child via props (Employee cards)
Line-by-line
import React from "react";
import Employee from "./Employee";


– Imports.

function App() {
  const employees = [
    { id: 101, name: "Rahul Sharma", dept: "HR" },
    { id: 102, name: "Sneha Patil", dept: "Finance" },
    { id: 103, name: "Amit Verma", dept: "IT" }
  ];


– Data array defined in parent.

  return (
    <div>
      <h2>Employee List</h2>
      {employees.map(emp => (
        <Employee key={emp.id} id={emp.id} name={emp.name} dept={emp.dept} />
      ))}
    </div>
  );
}
export default App;


– Renders one Employee per item; passes fields as props; uses id as key.

Employee.js

import React from "react";
function Employee(props) {
  return (
    <div style={{ border: "1px solid black", padding: "10px", margin: "10px" }}>
      <p><b>ID:</b> {props.id}</p>
      <p><b>Name:</b> {props.name}</p>
      <p><b>Department:</b> {props.dept}</p>
    </div>
  );
}
export default Employee;


– Receives props and displays them.

Theory (viva)

Props are read-only inputs from parent to child.

Reusability: a single component can render many cards with different data.

Key helps React reconcile lists efficiently.

For many nesting levels, consider Context to avoid prop drilling.

Has10 — Node.js FS (synchronous)
Line-by-line
const fs = require("fs");


– Import Node’s filesystem module.

fs.writeFileSync("data.txt", "Hello, this is first line.\n");
console.log("File created and data written.");


– Creates/overwrites data.txt synchronously; blocks until done.

fs.appendFileSync("data.txt", "This is appended text.\n");
console.log("Data appended.");


– Appends more content.

const content = fs.readFileSync("data.txt", "utf8");
console.log("File Content:\n", content);


– Reads file to string and logs it.

fs.unlinkSync("data.txt");
console.log("File deleted.");


– Deletes the file.

Theory (viva)

Sync APIs block the event loop—OK for scripts/tools, not for busy servers.

Always handle errors with try/catch in production.

Use "utf8" to read as string; otherwise you get a Buffer.

Has11 — Node.js FS (asynchronous, callbacks)
Line-by-line
const fs = require("fs");


– Filesystem module.

fs.writeFile("data.txt", "Hello! This is the initial file content.", () => {
  console.log("✅ Step 1: File created and data written.");


– Non-blocking write; callback runs after completion.

  fs.appendFile("data.txt", "\nThis is the appended content.", () => {
    console.log("✅ Step 2: Additional data appended.");


– Append after write finishes.

    fs.readFile("data.txt", "utf8", ( _ , data ) => {
      console.log("✅ Step 3: File content:\n");
      console.log(data);


– Read file, log content (ignoring err here for brevity).

      fs.unlink("data.txt", () => {
        console.log("\n✅ Step 4: File deleted.");
      });


– Delete after reading.

    });
  });
});


– Close nested callbacks.

Theory (viva)

Async I/O keeps Node responsive; callbacks run when operations finish.

Node callback signature: (err, data).

Avoid nested callbacks with Promises (fs.promises) or async/await.

Has12 — Streams: copy large file
Line-by-line
const fs = require("fs");
const readStream = fs.createReadStream("input.txt");
const writeStream = fs.createWriteStream("output.txt");


– Create readable and writable streams.

readStream.pipe(writeStream);


– Pipes data from read to write; manages backpressure automatically.

readStream.on("data", (chunk) => { 
  console.log("📦 Reading chunk:", chunk.length, "bytes");
});


– Logs each chunk size while reading.

readStream.on("end", () => { 
  console.log("✅ Streaming completed. Data copied to output.txt");
});


– Fires when the readable ends.

writeStream.on("finish", () => {
  console.log("✅ Write stream closed.");
});


– Fires after all data flushed to disk.

Theory (viva)

Streams process data chunk-by-chunk → low memory.

Backpressure: when writer is slower, .pipe() pauses/resumes automatically.

Important events: data, end, error, finish.

Has13 — Node Buffers
Line-by-line
const buf1 = Buffer.from("Hello Node");
console.log("🔹 Raw Buffer:", buf1);
console.log("🔹 Buffer as String:", buf1.toString());
console.log("🔹 Buffer as JSON:", buf1.toJSON());


– Create buffer from string (UTF-8). Log raw bytes, string form, and JSON view (byte array).

const buf2 = Buffer.alloc(10);
buf2.fill(65); // 'A'
console.log("🔹 Filled Buffer:", buf2);


– Zero-alloc 10 bytes then fill with 65.

buf2[0] = 90; // 'Z'
console.log("🔹 After modifying index 0:", buf2);


– Byte-level mutation.

const buf3 = Buffer.from(" World");
const result = Buffer.concat([buf1, buf3]);
console.log("🔹 Concatenated Buffer:", result.toString());


– Concatenate two buffers and print as string.

Theory (viva)

Buffer = raw binary data for files/sockets.

Default encoding for from(string) and toString() is utf8 unless specified.

Use Buffer.alloc / Buffer.from (safe) instead of deprecated constructors.

Useful for performance-critical binary operations.

Has14 — MongoDB Inventory CRUD (shell + Node)
Line-by-line (Mongo shell)
db.products.insertOne({
  name: "Laptop",
  category: "Electronics",
  price: 55000,
  stock: 10,
  createdAt: new Date("2025-01-10")
});


– Inserts a single product with fields including a BSON Date.

db.products.insertMany([
  { name: "Mobile Phone", category: "Mobile", price: 15000, stock: 30, createdAt: new Date("2024-12-15") },
  { name: "Headphones", category: "Audio", price: 2000, stock: 50, createdAt: new Date("2023-11-20") },
  { name: "Smart Watch", category: "Wearable", price: 4500, stock: 20, createdAt: new Date("2024-05-03") }
]);


– Inserts multiple docs at once.

db.products.find({ category: "Mobile" });


– Finds all where category equals "Mobile".

// If searching by name substring:
db.products.find({ name: /mobile/i });


– Regex search (case-insensitive).

db.products.deleteMany({ createdAt: { $lte: new Date("2024-12-31") } });


– Deletes all products created on/before 2024-12-31.

Line-by-line (Node driver)
const { MongoClient } = require("mongodb");


– Imports official driver.

const client = await MongoClient.connect("mongodb://127.0.0.1:27017");
const db = client.db("store");
const products = db.collection("products");


– Connects to server, selects DB and collection.

await products.insertOne({ ... });
await products.insertMany([ ... ]);


– Same operations as shell, but awaited.

console.log(await products.find({ category: "Mobile" }).toArray());


– Queries and materializes cursor to array for logging.

await products.deleteMany({ createdAt: { $lte: new Date("2024-12-31") } });
client.close();


– Deletes old docs and closes connection.

Theory (viva)

BSON Date lets you do proper range queries with $lte / $gte.

insertOne/Many, find, deleteMany are basic CRUD operations.

Regex queries enable substring searches; for large-scale text use text indexes.

Indexes on category and createdAt speed up queries and deletes.

Has15 — MongoDB Bookstore CRUD
Line-by-line
use bookstore;
db.createCollection("books");


– Selects DB; explicit create is optional (inserts create collections automatically).

db.books.insertOne({
  title: "The Alchemist",
  author: "Paulo Coelho",
  isbn: "9780061122415",
  publishedYear: 1988,
  genre: "Fiction",
  price: 299
});


– Inserts one book with all required fields.

db.books.insertMany([
  { title: "Atomic Habits", author: "James Clear", isbn: "9780735211292", publishedYear: 2018, genre: "Self-help", price: 450 },
  { title: "Rich Dad Poor Dad", author: "Robert Kiyosaki", isbn: "9781612680194", publishedYear: 1997, genre: "Finance", price: 350 }
]);


– Inserts multiple.

db.books.find();


– Lists all books.

db.books.findOne({ isbn: "9780061122415" });


– Fetches single by unique ISBN.

db.books.updateOne(
  { isbn: "9780061122415" },
  { $set: { price: 350, genre: "Motivational" } }
);


– Partially updates matching book.

db.books.deleteOne({ isbn: "9780061122415" });


– Deletes by unique ISBN.

Theory (viva)

CRUD: Create (insertOne/Many), Read (find/findOne), Update (updateOne with $set), Delete (deleteOne).

Uniqueness: enforce with an index:

db.books.createIndex({ isbn: 1 }, { unique: true })


Partial updates: $set changes only specified fields; preserves the rest.

Schema flexibility: MongoDB is schemaless by default; you can still enforce structure via validation or app code.

Quick Viva Cheats (use anywhere)

React

Re-renders happen when state or props change.

useEffect(fn, []) runs once after mount; useEffect(fn, [x]) runs when x changes.

useRef holds a mutable value that doesn’t trigger re-renders.

Controlled inputs: value={state} + onChange updates state.

Node

Use sync FS for small scripts; async FS/streams for servers and large data.

Streams handle data in chunks and manage backpressure.

MongoDB

Use BSON Date for time queries; prefer indexes matching query patterns.

Use $set for partial updates; ensure unique constraints with indexes.