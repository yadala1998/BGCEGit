/*
 * STEPReader.hpp
 *
 *  Created on: Oct 6, 2015
 *      Author: saumitra
 */

#ifndef READER_IGESREADER_HPP_
#define READER_IGESREADER_HPP_

#include <TopoDS_Shape.hxx>
#include <IGESControl_Reader.hxx>
#include <TransferBRep.hxx>
#include <Interface_Static.hxx>
#include <Standard_CString.hxx>

#include "Reader.hpp"
#include <string>
/*
 *
 */
class IGESReader: public Reader {
public:

	IGESReader(IGESControl_Reader* igesControlReader);
	virtual ~IGESReader();

	TopoDS_Shape read(std::string filename);
};

#endif /* READER_IGESREADER_HPP_ */

