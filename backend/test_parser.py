from parser import find_grading_scale, parse_courses, convert_to_5_scale

def test_grading_scale_extraction():
    text = """
    Grading Scale
    A 4.0
    A- 3.7
    B+ 3.5
    B 3.0
    """
    scale = find_grading_scale(text)
    assert scale['A'] == 4.0
    assert scale['B+'] == 3.5
    print("Grading scale test passed!")

def test_course_parsing():
    scale = {'A': 4.0, 'B': 3.0}
    text = """
    CS101 Intro to CS 3.0 A
    MATH101 Calculus 4.0 B
    """
    courses, gpa = parse_courses(text, scale)
    # CS101: 3.0 credits * 4.0 (A) = 12.0
    # MATH101: 4.0 credits * 3.0 (B) = 12.0
    # Total Points: 24.0. Total Credits: 7.0. GPA = 3.428
    
    assert len(courses) == 2
    assert abs(gpa - 3.428) < 0.01
    print("Course parsing test passed!")

def test_5_scale_conversion():
    # 4.0 on 4.0 scale -> 5.0 on 5.0 scale
    assert convert_to_5_scale(4.0, 4.0) == 5.0
    # 3.0 on 4.0 scale -> 3.75 on 5.0 scale
    assert convert_to_5_scale(3.0, 4.0) == 3.75
    print("Conversion test passed!")

def test_range_grading_scale():
    text = """
    GRADING SYSTEM
    Grades prior to 2001 : A(100~80), B(79~70), C(69~60), G(Success), N(Assignment)
    Grades effective 2002 : A+(100~90), A(89~80), B(79~70), C(69~60), P(Pass), N/T(Transferred Credits)
    """
    scale = find_grading_scale(text)
    # expect standard 5.0 scale keys
    assert 'A+' in scale
    assert scale['A+'] == 5.0 
    assert scale['A'] == 4.0
    print("Range grading scale test passed!")

if __name__ == "__main__":
    test_grading_scale_extraction()
    test_course_parsing()
    test_5_scale_conversion()
    test_range_grading_scale()
