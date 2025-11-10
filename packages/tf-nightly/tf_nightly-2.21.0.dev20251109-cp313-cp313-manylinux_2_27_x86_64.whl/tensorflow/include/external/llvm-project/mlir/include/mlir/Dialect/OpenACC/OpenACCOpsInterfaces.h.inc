/*===- TableGen'erated file -------------------------------------*- C++ -*-===*\
|*                                                                            *|
|* Interface Declarations                                                     *|
|*                                                                            *|
|* Automatically generated file, do not edit!                                 *|
|*                                                                            *|
\*===----------------------------------------------------------------------===*/

namespace mlir::acc {

/// An interface for compute and loop construct operations.
class ComputeRegionOpInterface;

} // namespace mlir::acc
namespace mlir::acc {

/// An interface for operations that access a partial entity such as
///     field or array element access.
class PartialEntityAccessOpInterface;

} // namespace mlir::acc
namespace mlir::acc {

/// An interface for compute and loop construct operations.
namespace detail {
struct ComputeRegionOpInterfaceInterfaceTraits {
  struct Concept {
    /// The methods defined by the interface.
    ::mlir::Block*(*getAllocaBlock)(const Concept *impl, ::mlir::Operation *);
  };
  template<typename ConcreteOp>
  class Model : public Concept {
  public:
    using Interface = ::mlir::acc::ComputeRegionOpInterface;
    Model() : Concept{getAllocaBlock} {}

    static inline ::mlir::Block*getAllocaBlock(const Concept *impl, ::mlir::Operation *tablegen_opaque_val);
  };
  template<typename ConcreteOp>
  class FallbackModel : public Concept {
  public:
    using Interface = ::mlir::acc::ComputeRegionOpInterface;
    FallbackModel() : Concept{getAllocaBlock} {}

    static inline ::mlir::Block*getAllocaBlock(const Concept *impl, ::mlir::Operation *tablegen_opaque_val);
  };
  template<typename ConcreteModel, typename ConcreteOp>
  class ExternalModel : public FallbackModel<ConcreteModel> {
  public:
    using ConcreteEntity = ConcreteOp;
  };
};
template <typename ConcreteOp>
struct ComputeRegionOpInterfaceTrait;

} // namespace detail
class ComputeRegionOpInterface : public ::mlir::OpInterface<ComputeRegionOpInterface, detail::ComputeRegionOpInterfaceInterfaceTraits> {
public:
  using ::mlir::OpInterface<ComputeRegionOpInterface, detail::ComputeRegionOpInterfaceInterfaceTraits>::OpInterface;
  template <typename ConcreteOp>
  struct Trait : public detail::ComputeRegionOpInterfaceTrait<ConcreteOp> {};

  /// Get alloca block
  ::mlir::Block*getAllocaBlock();
};

} // namespace mlir::acc
namespace mlir::acc {

/// An interface for operations that access a partial entity such as
///     field or array element access.
namespace detail {
struct PartialEntityAccessOpInterfaceInterfaceTraits {
  struct Concept {
    /// The methods defined by the interface.
    ::mlir::Value (*getBaseEntity)(const Concept *impl, ::mlir::Operation *);
    bool (*isCompleteView)(const Concept *impl, ::mlir::Operation *);
  };
  template<typename ConcreteOp>
  class Model : public Concept {
  public:
    using Interface = ::mlir::acc::PartialEntityAccessOpInterface;
    Model() : Concept{getBaseEntity, isCompleteView} {}

    static inline ::mlir::Value getBaseEntity(const Concept *impl, ::mlir::Operation *tablegen_opaque_val);
    static inline bool isCompleteView(const Concept *impl, ::mlir::Operation *tablegen_opaque_val);
  };
  template<typename ConcreteOp>
  class FallbackModel : public Concept {
  public:
    using Interface = ::mlir::acc::PartialEntityAccessOpInterface;
    FallbackModel() : Concept{getBaseEntity, isCompleteView} {}

    static inline ::mlir::Value getBaseEntity(const Concept *impl, ::mlir::Operation *tablegen_opaque_val);
    static inline bool isCompleteView(const Concept *impl, ::mlir::Operation *tablegen_opaque_val);
  };
  template<typename ConcreteModel, typename ConcreteOp>
  class ExternalModel : public FallbackModel<ConcreteModel> {
  public:
    using ConcreteEntity = ConcreteOp;
  };
};
template <typename ConcreteOp>
struct PartialEntityAccessOpInterfaceTrait;

} // namespace detail
class PartialEntityAccessOpInterface : public ::mlir::OpInterface<PartialEntityAccessOpInterface, detail::PartialEntityAccessOpInterfaceInterfaceTraits> {
public:
  using ::mlir::OpInterface<PartialEntityAccessOpInterface, detail::PartialEntityAccessOpInterfaceInterfaceTraits>::OpInterface;
  template <typename ConcreteOp>
  struct Trait : public detail::PartialEntityAccessOpInterfaceTrait<ConcreteOp> {};

  /// Get the base entity being accessed
  ::mlir::Value getBaseEntity();

  /// Check if this is a complete view of the entity
  bool isCompleteView();
};

} // namespace mlir::acc
namespace mlir::acc::detail {

  template <typename ConcreteOp>
  struct ComputeRegionOpInterfaceTrait : public ::mlir::OpInterface<ComputeRegionOpInterface, detail::ComputeRegionOpInterfaceInterfaceTraits>::Trait<ConcreteOp> {
  };

} // namespace mlir::acc::detail
namespace mlir::acc::detail {

  template <typename ConcreteOp>
  struct PartialEntityAccessOpInterfaceTrait : public ::mlir::OpInterface<PartialEntityAccessOpInterface, detail::PartialEntityAccessOpInterfaceInterfaceTraits>::Trait<ConcreteOp> {
  };

} // namespace mlir::acc::detail
namespace mlir::acc {

template<typename ConcreteOp>
::mlir::Block*detail::ComputeRegionOpInterfaceInterfaceTraits::Model<ConcreteOp>::getAllocaBlock(const Concept *impl, ::mlir::Operation *tablegen_opaque_val) {
  return &(llvm::cast<ConcreteOp>(tablegen_opaque_val)).getRegion().front();
}
template<typename ConcreteOp>
::mlir::Block*detail::ComputeRegionOpInterfaceInterfaceTraits::FallbackModel<ConcreteOp>::getAllocaBlock(const Concept *impl, ::mlir::Operation *tablegen_opaque_val) {
  return static_cast<const ConcreteOp *>(impl)->getAllocaBlock(tablegen_opaque_val);
}

} // namespace mlir::acc
namespace mlir::acc {

template<typename ConcreteOp>
::mlir::Value detail::PartialEntityAccessOpInterfaceInterfaceTraits::Model<ConcreteOp>::getBaseEntity(const Concept *impl, ::mlir::Operation *tablegen_opaque_val) {
  return (llvm::cast<ConcreteOp>(tablegen_opaque_val)).getBaseEntity();
}
template<typename ConcreteOp>
bool detail::PartialEntityAccessOpInterfaceInterfaceTraits::Model<ConcreteOp>::isCompleteView(const Concept *impl, ::mlir::Operation *tablegen_opaque_val) {
  return false;
}
template<typename ConcreteOp>
::mlir::Value detail::PartialEntityAccessOpInterfaceInterfaceTraits::FallbackModel<ConcreteOp>::getBaseEntity(const Concept *impl, ::mlir::Operation *tablegen_opaque_val) {
  return static_cast<const ConcreteOp *>(impl)->getBaseEntity(tablegen_opaque_val);
}
template<typename ConcreteOp>
bool detail::PartialEntityAccessOpInterfaceInterfaceTraits::FallbackModel<ConcreteOp>::isCompleteView(const Concept *impl, ::mlir::Operation *tablegen_opaque_val) {
  return static_cast<const ConcreteOp *>(impl)->isCompleteView(tablegen_opaque_val);
}

} // namespace mlir::acc
