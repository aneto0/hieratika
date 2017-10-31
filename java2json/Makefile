CLASSPATH=.:gson-2.6.2.jar
JFLAGS = 
JC = javac
JAVA = java
BUILD_DIR = build

.SUFFIXES: .java .class
.java.class:
	$(JC) $(JFLAGS) -cp $(CLASSPATH) -d $(BUILD_DIR) $*.java

CLASSES = \
	JavaToJson.java  \
	PMCVariable.java  \
	PMCGap.java  \
	PMCShape.java \
	PMCTest0.java \
	PMCTestStruct1.java \
	PMCTestStruct2.java \
	PMCTestStruct3.java \
	PlantDEMO0.java \
	Plant55A0.java

default: classes

classes: $(CLASSES:.java=.class)

clean:
	$(RM) $(BUILD_DIR)/*.class
