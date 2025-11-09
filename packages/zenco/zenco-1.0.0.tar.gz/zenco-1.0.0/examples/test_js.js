let message = "Hello from a sample JavaScript file!";

function greetUser(name) {
  return `Hello, ${name}! Welcome to the world of JavaScript.`;
}
let greeting = greetUser("User");

console.log(message);
console.log(greeting);

let sum = num1 + num2;
console.log(`The sum of ${num1} and ${num2} is: ${sum}`);

if (sum > 10) {
  console.log("The sum is greater than 10.");
} else {
  console.log("The sum is not greater than 10.");
}

console.log("Counting from 1 to 3:");
for (let i = 1; i <= 3; i++) {
  console.log(i);
}