/*===- TableGen'erated file -------------------------------------*- C++ -*-===*\
|*                                                                            *|
|* Interface Definitions                                                      *|
|*                                                                            *|
|* Automatically generated file, do not edit!                                 *|
|*                                                                            *|
\*===----------------------------------------------------------------------===*/


/// Get alloca block
::mlir::Block*mlir::acc::ComputeRegionOpInterface::getAllocaBlock() {
      return getImpl()->getAllocaBlock(getImpl(), getOperation());
  }

/// Get the base entity being accessed
::mlir::Value mlir::acc::PartialEntityAccessOpInterface::getBaseEntity() {
      return getImpl()->getBaseEntity(getImpl(), getOperation());
  }

/// Check if this is a complete view of the entity
bool mlir::acc::PartialEntityAccessOpInterface::isCompleteView() {
      return getImpl()->isCompleteView(getImpl(), getOperation());
  }
