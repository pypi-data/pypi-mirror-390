def greet(name):
    return f"Welcome, {name}! This module is called expreess."



# 1. Build interactive UI blocks using hooks, refs, usestate(), useeffect() in React front
# endApplication
# App.js
# import React, { useState, useEffect, useRef } from "react";
# function App() {
# // 🔹 useState - to change color when clicked
# const [color, setColor] = useState("lightblue");
# // 🔹 useEffect - to update timer every second
# const [time, setTime] = useState(0);
# useEffect(() => {
# const timer = setInterval(() => setTime((t) => t + 1), 1000);
# return () => clearInterval(timer); // cleanup on unmount
# }, []);
# // 🔹 useRef - to access input directly
# const inputRef = useRef(null);
# // 🔹 useEffect - to focus input automatically when component loads
# useEffect(() => {
# inputRef.current.focus(); // focus input on page load
# }, []);
# return (
# <div>
# <h2>React Hooks Example (useState, useEffect, useRef)</h2>
# {/* useState Example */}
# <div
# style={{ backgroundColor: color, padding: "10px", margin: "10px" }}
# onClick={() =>
# setColor(color === "lightblue" ? "lightcoral" : "lightblue")
# }
# >
# Click me to change color (useState)
# </div>
# {/* useEffect Example */}
# <p>Timer using useEffect: {time} seconds</p>
# {/* useRef Example - Input auto focuses on load */}
# <input ref={inputRef} type="text" placeholder="Input auto-focused" />
# </div>
# );
# }
# export default App;
# 2. Use functional components for reusable UI elements like headers, footers, and
# navigation bars.
# App.js
# import React from "react";
# import Header from "./Header";
# import Navbar from "./Navbar";
# import Footer from "./Footer";
# function App() {
# return (
# <div>
# <Header />
# <Navbar />
# <h2>Welcome to My Website</h2>
# <p>This is a simple example using functional components in React.</p>
# <Footer />
# </div>
# );
# }
# export default App;
# Header.js
# function Header() {
# return <h1>My Website</h1>;
# }
# export default Header;
# Navbar.js
# function Navbar() {
# return (
# <nav>
# <a href="#home">Home</a> |
# <a href="#about">About</a> |
# <a href="#contact">Contact</a>
# </nav>
# );
# }
# export default Navbar;
# Footer.js
# function Footer() {
# return (
# <footer>
# <p>&copy; 2025 All Rights Reserved</p>
# </footer>
# );
# }
# export default Footer;
# 3. Implement a form to add new student details (Name, Roll No, Department)and Display
# the entered student records dynamically using a list component.
# App.js
# import React, { useState } from "react";
# import './App.css';
# function StudentForm() {
# const [students, setStudents] = useState([]);
# const [form, setForm] = useState({ name: "", rollNo: "", department: "" });
# const handleChange = (e) => setForm({ ...form, [e.target.name]: e.target.value });
# const handleSubmit = (e) => {
# e.preventDefault();
# setStudents([...students, form]);
# setForm({ name: "", rollNo: "", department: "" });
# };
# return (
# <div>
# <form onSubmit={handleSubmit}>
# <input name="name"
# placeholder="Name"
# value={form.name}
# onChange={handleChange} required />
# <input name="rollNo"
# placeholder="Roll No"
# value={form.rollNo}
# onChange={handleChange} required />
# <input name="department"
# placeholder="Department"
# value={form.department}
# onChange={handleChange} required />
# <button type="submit">Add</button>
# </form>
# <ul>
# {students.map((s, i) => <li key={i}>
# {s.name} - {s.rollNo} - {s.department}</li>)}
# </ul>
# </div>
# );
# }
# export default StudentForm;
# 4. Include navigation between Home, Register, and Registered Users pages using
# React Router.
# 5. Design a functional component that uses useState() to manage a list of tasks.
# App.js
# import React, { useState } from "react";
# import "./App.css";
# function App() {
# // Step 1: Create a state variable to store tasks
# const [task, setTask] = useState("");
# const [taskList, setTaskList] = useState([]);
# // Step 2: Function to add new task
# const addTask = () => {
# if (task.trim() !== "") {
# setTaskList([...taskList, task]);
# setTask(""); // clear input after adding
# }
# };
# return (
# <div className="App">
# <h1>📝 Task Manager using useState()</h1>
# {/* Input field and button */}
# <input
# type="text"
# placeholder="Enter new task"
# value={task}
# onChange={(e) => setTask(e.target.value)}
# />
# <button onClick={addTask}>Add Task</button>
# {/* Display tasks */}
# <ul>
# {taskList.map((item, index) => (
# <li key={index}>
# <input type="checkbox" /> {item}
# </li>
# ))}
# </ul>
# </div>
# );
# }
# export default App;
# App.css
# .App {
# text-align: center;
# margin-top: 40px;
# font-family: Arial, sans-serif;
# }
# input[type="text"] {
# padding: 6px;
# width: 220px;
# margin-right: 8px;
# border-radius: 4px;
# border: 1px solid #ccc;
# font-size: 15px;
# }
# button {
# padding: 7px 14px;
# border: none;
# background-color: #333;
# color: white;
# border-radius: 5px;
# cursor: pointer;
# font-size: 15px;
# }
# button:hover {
# background-color: #555;
# }
# ul {
# list-style-type: none;
# padding: 0;
# width: 300px;
# margin: 20px auto;
# }
# li {
# margin: 8px 0;
# display: flex;
# align-items: center;
# justify-content: flex-start;
# gap: 10px;
# font-size: 16px;
# text-align: left;
# }
# h1 {
# font-size: 26px;
# display: flex;
# justify-content: center;
# align-items: center;
# gap: 10px;
# }
# h1::before {
# content: "📝";
# font-size: 28px;
# }
# 6. Use useRef() to automatically focus the input box when the page loads.
# Answer:
# AutoFocusInput.js
# import React, { useEffect, useRef } from "react";
# function AutoFocusInput() {
# const inputRef = useRef(null); // Step 1: Create ref
# useEffect(() => {
# inputRef.current.focus(); // Step 2: Focus input when page loads
# }, []);
# return (
# <div>
# <h2>Auto Focus Input Example</h2>
# <input ref={inputRef} type="text" placeholder="Type here..." />
# </div>
# );
# }
# export default AutoFocusInput;
# app.js
# import React from "react";
# import AutoFocusInput from "./AutoFocusInput";
# function App() {
# return <AutoFocusInput />;
# }
# export default App;
# 7. Use useEffect() to update the clock every second.
# App.js
# import React, { useState, useEffect } from "react";
# function App() {
#  const [time, setTime] = useState(new Date().toLocaleTimeString());
#  useEffect(() => {
#  const timer = setInterval(() => {
#  setTime(new Date().toLocaleTimeString());
#  }, 1000);
#  return () => clearInterval(timer); // cleanup
#  }, []);
#  return (
#  <div style={{ textAlign: "center", marginTop: "50px" }}>
#  <h2>Current Time</h2>
#  <h1>{time}</h1>
#  </div>
#  );
# }
# export default App;
# OUTPUT :
# 8. Create a json file to store data and fetch using list component
# app.js
# import React, { useEffect, useState } from "react";
# function App() {
# const [data, setData] = useState([]);
# useEffect(() => {
# fetch("/data.json")
# .then((res) => res.json())
# .then((d) => setData(d));
# }, []);
# return (
# <div>
# <h2>Tech Stack</h2>
# <ul>
# {data.map((item) => (
# <li key={item.id}>{item.name}</li>
# ))}
# </ul>
# </div>
# );
# }
# export default App;
# Data.json
# [
# { "id": 1, "name": "React" },
# { "id": 2, "name": "Node.js" },
# { "id": 3, "name": "MongoDB" }
# ]
# 9. Create a parent component (App.js) to hold employee data, Pass data (Employee Name,
# ID, Department) to a child component (Employee.js) using props and Display at least
# three employee cards dynamically using the same reusable component.
# Employee.js
# import React from "react";
# import "./Employee.css";
# // Employee is a reusable card component that receives props
# function Employee({ name, id, dept}) {
#  return (
#  <div className="emp-card">
#  <h3 className="emp-name">{name}</h3>
#  <p>ID: <strong>{id}</strong></p>
#  <p>Department: <em>{dept}</em></p>
#  </div>
#  );
# }
# export default Employee;
# Employee.css
# /* simple card styling */
# .emp-card {
#  border: 1px solid #ccc;
#  padding: 12px;
#  border-radius: 8px;
#  width: 200px;
#  box-shadow: 0 1px 4px rgba(0,0,0,0.08);
#  margin: 8px;
# }
# .emp-name { margin: 0 0 8px 0; }
# App.js
# import React from "react";
# import Employee from "./components/Employee";
# function App() {
#  // parent holds employee data
#  const employees = [
#  { name: "Purva ", id: "E101", dept: "IT" },
#  { name: "Tej Mehta", id: "E102", dept: "DevOps" },
#  { name: "Avi Patel", id: "E103", dept: "QA" }
#  ];
#  return (
#  <div style={{ padding: 20 }}>
#  <h2>Employee Directory</h2>
#  {/* render cards dynamically using map */}
#  <div style={{ display: "flex", flexWrap: "wrap" }}>
#  {employees.map((emp) => (
#  <Employee
#  key={emp.id} // unique key for list rendering
#  name={emp.name}
#  id={emp.id}
#  dept={emp.dept}
#  />
#  ))}
#  </div>
#  </div>
#  );
# }
# export default App;
# 10. Perform the following operations using synchronous
# Create and write data to a file named data.txt.
# Append additional content to the same file.
# Read the content of the file and display it in the console.
# Delete the file after reading.
# app.js
# // Import the 'fs' (File System) module
# const fs = require("fs");
# // Step 1: Create and Write Data to a File (Synchronous)
# fs.writeFileSync("data.txt", "Hello! This is the initial file content.");
# console.log("✅ Step 1: File created and data written successfully.");
# // Step 2: Append Additional Content to the Same File (Synchronous)
# fs.appendFileSync("data.txt", "\nThis is the appended content.");
# console.log("✅ Step 2: Additional data appended successfully.");
# // Step 3: Read the Content of the File and Display It (Synchronous)
# const data = fs.readFileSync("data.txt", "utf8");
# console.log("✅ Step 3: Reading file content...\n");
# console.log(data);
# // Step 4: Delete the File after Reading (Synchronous)
# fs.unlinkSync("data.txt");
# console.log("✅ Step 4: File deleted successfully.");
# 11. Perform the following operations using asynchronous
# Create and write data to a file named data.txt.
# Append additional content to the same file.
# Read the content of the file and display it in the console.
# Delete the file after reading.
# app.js
# const fs = require('fs/promises');
# async function fileOps() {
# const file = 'data.txt';
# try {
# // Create/write initial data
# await fs.writeFile(file, 'Hello, this is the initial content.\n');
# // Append more content
# await fs.appendFile(file, 'This is appended content.\n');
# // Read and display content
# const content = await fs.readFile(file, 'utf8');
# console.log(content);
# // Delete the file
# await fs.unlink(file);
# } catch (err) {
# console.error(err);
# }
# }
# fileOps();
# 12. Create a Node.js script Use Readable and Writable Streams to perform following
# operation
# Read data from a large file (input.txt)
# Write the streamed data into another file (output.txt)
# Code:
# app.js
# const fs = require("fs");
# // Create readable stream from input.txt
# const readStream = fs.createReadStream("input.txt");
# // Create writable stream to output.txt
# const writeStream = fs.createWriteStream("output.txt");
# // Pipe read data directly into write stream
# readStream.pipe(writeStream);
# readStream.on("data", (chunk) => {
#  console.log("📦 Reading chunk:", chunk.length, "bytes");
# });
# readStream.on("end", () => {
#  console.log("✅ Data copied successfully to output.txt");
# });
# 13. Create a Node.js file named bufferExample.js.Perform the following tasks:
# Create a Buffer from a string
# Display the buffer content in raw, string, and JSON format.
# Create an empty buffer of size 10 and fill it with a value.
# Modify buffer content using indexing.
# Concatenate two buffers and display the result.
# app.js
# // 1️⃣Create a Buffer from a string
# const buf1 = Buffer.from("Hello Node");
# // Display buffer in raw format
# console.log("Raw Buffer:", buf1);
# // Display buffer as string
# console.log("String Format:", buf1.toString());
# // Display buffer as JSON
# console.log("JSON Format:", buf1.toJSON());
# // 2️⃣Create an empty buffer of size 10 and fill it
# const buf2 = Buffer.alloc(10);
# buf2.fill(65); // ASCII for 'A'
# console.log("Filled Buffer:", buf2, " =>", buf2.toString());
# // 3️⃣Modify buffer content using indexing
# buf2[0] = 90; // ASCII for 'Z'
# console.log("After Modification:", buf2, "=>", buf2.toString());
# // 4️⃣Concatenate two buffers
# const buf3 = Buffer.from(" Buffer Test");
# const result = Buffer.concat([buf1, buf3]);
# console.log("Concatenated Buffer:", result);
# console.log("Concatenated String:", result.toString());
# .
# 14. MongoDB CRUD operations. Build an inventory management database for a small
# electronics store. insert a new product with fields like name, category, price, stock, and
# created At into the products collection.Delete the product with created At date on or
# before 2024.Use InsertOne and InsertMany. Use find method to search Mobile phones
# from products.
# Ans:
# Step 1: Open MongoDB Compass
# 1. Open MongoDB Compass.
# Connect to your local server → usually it’s:
# mongodb://localhost:27017
# 2. Once connected, click on “Create Database”.
# Step 2: Create Database & Collection
# ● Database Name: electronicsStore
# ● Collection Name: products
# Then click Create Database.
# Insert One Product (InsertOne)
# Now you’ll insert a single product manually or using the Insert Document button.
# Option 1 (GUI):
# 1. Open the products collection.
# 2. Click Insert Document.
# 3. Paste this JSON:
# {
# "name": "iPhone 15",
# "category": "Mobile",
# "price": 79999,
# "stock": 15,
# "createdAt": { "$date": "2025-01-10T00:00:00Z" }
# }
# 4. Click Insert
# Option 2 (Shell inside Compass):
# Run:
# db.products.insertOne({
# name: "iPhone 15",
# category: "Mobile",
# price: 79999,
# stock: 15,
# createdAt: new Date("2025-01-10")
# });
# Insert Many Products (InsertMany)
# In the Command tab or Mongo Shell, run:
# use electronicsStore (First run this)
# db.products.insertMany([
# {
# name: "Samsung Galaxy S23",
# category: "Mobile",
# price: 74999,
# stock: 20,
# createdAt: new Date("2023-12-15")
# },
# {
# name: "HP Pavilion Laptop",
# category: "Laptop",
# price: 55999,
# stock: 10,
# createdAt: new Date("2024-02-20")
# },
# {
# name: "Sony Headphones",
# category: "Accessories",
# price: 4999,
# stock: 50,
# createdAt: new Date("2025-03-10")
# }
# ]);
# Step 3 : Check if It’s Inserted
# Run:
# use electronicsStore
# db.products.find()
# Step 4: Find Mobiles
# Run:
# db.products.find({ category: "Mobile" })
# Step 5: Delete Old Products (Before 2025)
# Run:
# db.products.deleteMany({
#  createdAt: { $lte: new Date("2024-12-31") }
# })
# Step 6: To check if Old Products are deleted (Before 2025)
# Run:
# db.products.find()