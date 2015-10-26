/*
 * VoxelShape.cpp
 *
 *  Created on: Oct 12, 2015
 *      Author: friedrich
 */

#include "VoxelShape.hpp"


VoxelShape::VoxelShape(){};

VoxelShape::VoxelShape(Voxel_BoolDS voxelShape,
		std::vector<double> origin): _voxelShape(voxelShape), _origin(origin) {
}

VoxelShape::~VoxelShape() {
	// TODO Auto-generated destructor stub
	//_voxelShape.Destroy();
}

double VoxelShape::getOriginX() {
	return _origin[0];
}

double VoxelShape::getOriginY() {
	return _origin[1];
}

double VoxelShape::getOriginZ() {
	return _origin[2];
}

Voxel_BoolDS& VoxelShape::getVoxelShape() {
	return _voxelShape;
}

const std::vector<double>& VoxelShape::getOrigin() const {
	return _origin;
}

void VoxelShape::setOrigin(const std::vector<double> origin) {
	_origin = origin;
}

void VoxelShape::setVoxelShape(const Voxel_BoolDS voxelShape) {
	_voxelShape = voxelShape;
}

const std::vector<double>& VoxelShape::getDimension() const {
	return _dimension;
}

void VoxelShape::setDimension(const std::vector<double> dimension) {
	_dimension = dimension;
}

VoxelShape& VoxelShape::operator=( const VoxelShape& other ) {
	      this->_voxelShape = other._voxelShape;
	      this->_dimension = other._dimension;
	      this->_origin = other._origin;
	      return *this;
}

const std::vector<int>& VoxelShape::getIndices() const {
	return _indices;
}

void VoxelShape::setIndices(const std::vector<int> indices) {
	_indices = indices;
}

Voxel_BoolDS VoxelShape::copyVoxelShape() {
	return _voxelShape;
}

const std::vector<int> VoxelShape::getVoxelDimension() const {
	return _voxelDimension;
}

void VoxelShape::setVoxelDimension(const std::vector<int> voxelDimension) {
	_voxelDimension = voxelDimension;
}

double VoxelShape::getXLen() {
	return _voxelShape.GetXLen();
}

double VoxelShape::getYLen() {
	return _voxelShape.GetYLen();
}

double VoxelShape::getZLen() {
	return _voxelShape.GetZLen();
}

int VoxelShape::getNbX() {
	return _voxelShape.GetNbX();
}

int VoxelShape::getNbY() {
	return _voxelShape.GetNbY();
}

int VoxelShape::getNbZ() {
	return _voxelShape.GetNbZ();
}

bool VoxelShape::isVoxel(int x, int y, int z) {
	return _voxelShape.Get(x,y,z);
}

void VoxelShape::setVoxel(int x, int y, int z, bool isVoxel) {
	_voxelShape.Set(x, y, z, isVoxel);
}
