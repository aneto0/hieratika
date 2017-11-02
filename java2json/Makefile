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
	PMCDiscreteCoil.java  \
	PMCLibrary.java  \
	PMCShape.java \
	PMCTest0.java \
	PMCTestStruct1.java \
	PMCTestStruct2.java \
	PMCTestStruct3.java \
	PlantDEMO0.java \
	P55A3DiscreteCoils.java \
	P55A4DiscreteCoils.java \
	P55A5DiscreteCoils.java \
	P55A6DiscreteCoils.java \
	P55A9DiscreteCoils.java \
	P55AADiscreteCoils.java \
	P55ABDiscreteCoils.java \
	P55ACDiscreteCoils.java \
	P55AGDiscreteCoils.java \
	P55AJDiscreteCoils.java \
	P55AKDiscreteCoils.java \
	P55ALDiscreteCoils.java \
	P55APDiscreteCoils.java	\
	P55A0DiscreteCoils.java \
	Plant55A0.java

default: classes

classes: $(CLASSES:.java=.class)

clean:
	$(RM) $(BUILD_DIR)/*.class
