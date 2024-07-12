//===================================================================================================================
/* Q1. Solve this in SQL:

 Write a query to return a list of professor names and their associated courses
 for all courses outside of their departments. There should be no duplicate rows,
 but they can be in any order.

 The output should contain two columns: professor.name, course.name.

 Schema:

 PROFESSOR
 Name            Type        Description
 ID              Integer     unique id, primary key
 NAME            String      
 DEPARTMENT_ID   Integer     foreign key, department.id
 SALARY          Integer     

 DEPARTMENT
 Name            Type        Description
 ID              Integer     unique id, primary key
 NAME            String      

 COURSE
 Name            Type        Description
 ID              Integer     unique id, primary key
 NAME            String      
 DEPARTMENT_ID   Integer     foreign key, department.id
 CREDITS         Integer     

 SCHEDULE
 Name            Type        Description
 PROFESSOR_ID    Integer     foreign key, professor.id
 COURSE_ID       Integer     foreign key, course.id
 SEMESTER        Integer     
 YEAR            Integer     

 Sample Data Tables:

 PROFESSOR
 ID  NAME              DEPARTMENT_ID  SALARY
 1   Alex Daniels      4              7169
 2   Drew Knight       1              9793
 3   Jordan Myers      4              25194
 4   Tyler Rodriguez   3              9686
 5   Blake Gome        2              30860
 6   Spencer George    5              10487
 7   Ellis Vasquez     4              6353
 8   Morgan Flores     1              25796
 9   Riley Gilbert     5              35678
 10  Peyton Stevens    2              26648

 DEPARTMENT
 ID  NAME
 3   Biological Sciences
 5   Technology
 6   Humanities & Social Sciences
 2   Clinical Medicine
 4   Arts and Humanities
 1   Physical Sciences

 COURSE
 ID  NAME                                            DEPARTMENT_ID  CREDITS
 9   Clinical Biochemistry                           2              3
 4   Astronomy                                       1              6
 10  Clinical Neuroscience                           2              5
 1   Pure Mathematics and Mathematical Statistics    1              3
 6   Geography                                       1              7
 8   Chemistry                                       1              1
 5   Physics                                         1              8
 3   Earth Science                                   1              7
 7   Materials Science and Metallurgy                1              5
 2   Applied Mathematics and Theoretical Physics     1              5

 SCHEDULE
 PROFESSOR_ID  COURSE_ID  SEMESTER  YEAR
 4             4          3         2003
 3             3          1         2011
 1             7          5         2011
 7             7          1         2010
 4             6          1         2001
 9             3          1         2012
 10            2          4         2009
 1             1          3         2014
 1             2          3         2008
 1             7          5         2007

 Sample Output:
 Tyler Rodriguez    Astronomy
 Jordan Myers       Earth Sciences
 Alex Daniels       Materials Science and Metallurgy
 Ellis Vasquez      Materials Science and Metallurgy
 Tyler Rodriguez    Geography
 Riley Gilbert      Earth Sciences
 Peyton Stevens     Applied Mathematics and Theoretical Physics
 Alex Daniels       Pure Mathematics and Mathematical Statistics
 Alex Daniels       Applied Mathematics and Theoretical Physics
 Alex Daniels       Materials Science and Metallurgy 

 Explanation:

 Example logic
     Professor Tyler Rodriguez's department_id is 3, but the Astronomy course's department_id is 1.
     Professor Jordan Myers's department_id is 4, but the Earth Sciences course's department_id is 1

*/ //=================================================================================================================

//To solve this problem in SQL, you can use a combination of JOIN operations to connect the PROFESSOR, DEPARTMENT, COURSE, and SCHEDULE tables. You'll want to find professors who have taught courses outside of their own department. This involves comparing the DEPARTMENT_ID of the professor with the DEPARTMENT_ID of the course they taught. Here's how you can write the SQL query:

SELECT DISTINCT p.NAME AS professor_name, c.NAME AS course_name
FROM PROFESSOR p
JOIN SCHEDULE s ON p.ID = s.PROFESSOR_ID
JOIN COURSE c ON s.COURSE_ID = c.ID
WHERE p.DEPARTMENT_ID!= c.DEPARTMENT_ID
ORDER BY professor_name, course_name;
Here's a breakdown of what this query does:

//SELECT DISTINCT: This selects unique combinations of professor and course names. The DISTINCT keyword ensures that each row in the result set represents a unique pair of professor and course, eliminating duplicates.

//FROM PROFESSOR p JOIN SCHEDULE s ON p.ID = s.PROFESSOR_ID: This joins the PROFESSOR table with the SCHEDULE table based on the professor's ID. The alias p is used for the PROFESSOR table and s for the SCHEDULE table to make the query more readable.

//JOIN COURSE c ON s.COURSE_ID = c.ID: This further joins the result with the COURSE table based on the course ID. The alias c is used for the COURSE table.
//WHERE p.DEPARTMENT_ID!= c.DEPARTMENT_ID: This condition filters the results to include only those rows where the professor's department ID does not match the course's department ID, thus finding courses taught outside of the professor's department.
//ORDER BY professor_name, course_name: This orders the results first by professor name and then by course name. While the requirement specifies "they can be in any order," ordering by both professor and course names provides a consistent and understandable presentation of the results.
//This query effectively retrieves a list of professor names and their associated courses for all courses outside of their departments, without duplicates, and in a readable order.