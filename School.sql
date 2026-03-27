CREATE TABLE Students (
    student_id int PRIMARY KEY,
    name varchar(100),
    major varchar(50),
    gpa float
);

CREATE TABLE Courses (
    course_id int PRIMARY KEY,
    title varchar(100),
    credits int
);

CREATE TABLE Enrollments (
    enrollment_id int PRIMARY KEY,
    student_id int REFERENCES Students(student_id),
    course_id int REFERENCES Courses(course_id),
    grade varchar(2)
);
