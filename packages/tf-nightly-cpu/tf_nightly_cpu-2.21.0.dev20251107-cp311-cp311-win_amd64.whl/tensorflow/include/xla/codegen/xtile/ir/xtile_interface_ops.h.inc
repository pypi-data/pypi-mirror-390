/*===- TableGen'erated file -------------------------------------*- C++ -*-===*\
|*                                                                            *|
|* Interface Declarations                                                     *|
|*                                                                            *|
|* Automatically generated file, do not edit!                                 *|
|*                                                                            *|
\*===----------------------------------------------------------------------===*/

namespace xla::xtile {
class TiledBufferInterface;
} // namespace xla::xtile
namespace xla::xtile {
namespace detail {
struct TiledBufferInterfaceInterfaceTraits {
  struct Concept {
    /// The methods defined by the interface.
    mlir::TypedValue<mlir::MemRefType> (*getBuffer)(const Concept *impl, ::mlir::Operation *);
    mlir::TypedValue<mlir::RankedTensorType> (*getTile)(const Concept *impl, ::mlir::Operation *);
    mlir::ValueRange (*getOffsets)(const Concept *impl, ::mlir::Operation *);
    llvm::ArrayRef<int64_t> (*getFullTileShape)(const Concept *impl, ::mlir::Operation *);
    llvm::ArrayRef<int64_t> (*getStrides)(const Concept *impl, ::mlir::Operation *);
  };
  template<typename ConcreteOp>
  class Model : public Concept {
  public:
    using Interface = ::xla::xtile::TiledBufferInterface;
    Model() : Concept{getBuffer, getTile, getOffsets, getFullTileShape, getStrides} {}

    static inline mlir::TypedValue<mlir::MemRefType> getBuffer(const Concept *impl, ::mlir::Operation *tablegen_opaque_val);
    static inline mlir::TypedValue<mlir::RankedTensorType> getTile(const Concept *impl, ::mlir::Operation *tablegen_opaque_val);
    static inline mlir::ValueRange getOffsets(const Concept *impl, ::mlir::Operation *tablegen_opaque_val);
    static inline llvm::ArrayRef<int64_t> getFullTileShape(const Concept *impl, ::mlir::Operation *tablegen_opaque_val);
    static inline llvm::ArrayRef<int64_t> getStrides(const Concept *impl, ::mlir::Operation *tablegen_opaque_val);
  };
  template<typename ConcreteOp>
  class FallbackModel : public Concept {
  public:
    using Interface = ::xla::xtile::TiledBufferInterface;
    FallbackModel() : Concept{getBuffer, getTile, getOffsets, getFullTileShape, getStrides} {}

    static inline mlir::TypedValue<mlir::MemRefType> getBuffer(const Concept *impl, ::mlir::Operation *tablegen_opaque_val);
    static inline mlir::TypedValue<mlir::RankedTensorType> getTile(const Concept *impl, ::mlir::Operation *tablegen_opaque_val);
    static inline mlir::ValueRange getOffsets(const Concept *impl, ::mlir::Operation *tablegen_opaque_val);
    static inline llvm::ArrayRef<int64_t> getFullTileShape(const Concept *impl, ::mlir::Operation *tablegen_opaque_val);
    static inline llvm::ArrayRef<int64_t> getStrides(const Concept *impl, ::mlir::Operation *tablegen_opaque_val);
  };
  template<typename ConcreteModel, typename ConcreteOp>
  class ExternalModel : public FallbackModel<ConcreteModel> {
  public:
    using ConcreteEntity = ConcreteOp;
  };
};
template <typename ConcreteOp>
struct TiledBufferInterfaceTrait;

} // namespace detail
class TiledBufferInterface : public ::mlir::OpInterface<TiledBufferInterface, detail::TiledBufferInterfaceInterfaceTraits> {
public:
  using ::mlir::OpInterface<TiledBufferInterface, detail::TiledBufferInterfaceInterfaceTraits>::OpInterface;
  template <typename ConcreteOp>
  struct Trait : public detail::TiledBufferInterfaceTrait<ConcreteOp> {};

  /// Get the memref value of the buffer.
  mlir::TypedValue<mlir::MemRefType> getBuffer();

  /// Get the tensor value of the tile.
  mlir::TypedValue<mlir::RankedTensorType> getTile();

  /// Get the offsets into the buffer.
  mlir::ValueRange getOffsets();

  /// Get the full unreduced tile shape.
  llvm::ArrayRef<int64_t> getFullTileShape();

  /// Get the stride lengths of the buffer.
  llvm::ArrayRef<int64_t> getStrides();

    // Returns the set of unit dimensions that are removed from the tile
    // dimensions.
    llvm::SmallDenseSet<unsigned> getReducedDimensions();
};
} // namespace xla::xtile
namespace xla::xtile::detail {
  template <typename ConcreteOp>
  struct TiledBufferInterfaceTrait : public ::mlir::OpInterface<TiledBufferInterface, detail::TiledBufferInterfaceInterfaceTraits>::Trait<ConcreteOp> {

    llvm::SmallDenseSet<unsigned> getReducedDimensions() {
      return static_cast<TiledBufferInterface>((*static_cast<ConcreteOp *>(this))).getReducedDimensions();
    }
  
  };
} // namespace xla::xtile::detail
namespace xla::xtile {
template<typename ConcreteOp>
mlir::TypedValue<mlir::MemRefType> detail::TiledBufferInterfaceInterfaceTraits::Model<ConcreteOp>::getBuffer(const Concept *impl, ::mlir::Operation *tablegen_opaque_val) {
  return (llvm::cast<ConcreteOp>(tablegen_opaque_val)).getBuffer();
}
template<typename ConcreteOp>
mlir::TypedValue<mlir::RankedTensorType> detail::TiledBufferInterfaceInterfaceTraits::Model<ConcreteOp>::getTile(const Concept *impl, ::mlir::Operation *tablegen_opaque_val) {
  return (llvm::cast<ConcreteOp>(tablegen_opaque_val)).getTile();
}
template<typename ConcreteOp>
mlir::ValueRange detail::TiledBufferInterfaceInterfaceTraits::Model<ConcreteOp>::getOffsets(const Concept *impl, ::mlir::Operation *tablegen_opaque_val) {
  return (llvm::cast<ConcreteOp>(tablegen_opaque_val)).getOffsets();
}
template<typename ConcreteOp>
llvm::ArrayRef<int64_t> detail::TiledBufferInterfaceInterfaceTraits::Model<ConcreteOp>::getFullTileShape(const Concept *impl, ::mlir::Operation *tablegen_opaque_val) {
  return (llvm::cast<ConcreteOp>(tablegen_opaque_val)).getFullTileShape();
}
template<typename ConcreteOp>
llvm::ArrayRef<int64_t> detail::TiledBufferInterfaceInterfaceTraits::Model<ConcreteOp>::getStrides(const Concept *impl, ::mlir::Operation *tablegen_opaque_val) {
  return (llvm::cast<ConcreteOp>(tablegen_opaque_val)).getStrides();
}
template<typename ConcreteOp>
mlir::TypedValue<mlir::MemRefType> detail::TiledBufferInterfaceInterfaceTraits::FallbackModel<ConcreteOp>::getBuffer(const Concept *impl, ::mlir::Operation *tablegen_opaque_val) {
  return static_cast<const ConcreteOp *>(impl)->getBuffer(tablegen_opaque_val);
}
template<typename ConcreteOp>
mlir::TypedValue<mlir::RankedTensorType> detail::TiledBufferInterfaceInterfaceTraits::FallbackModel<ConcreteOp>::getTile(const Concept *impl, ::mlir::Operation *tablegen_opaque_val) {
  return static_cast<const ConcreteOp *>(impl)->getTile(tablegen_opaque_val);
}
template<typename ConcreteOp>
mlir::ValueRange detail::TiledBufferInterfaceInterfaceTraits::FallbackModel<ConcreteOp>::getOffsets(const Concept *impl, ::mlir::Operation *tablegen_opaque_val) {
  return static_cast<const ConcreteOp *>(impl)->getOffsets(tablegen_opaque_val);
}
template<typename ConcreteOp>
llvm::ArrayRef<int64_t> detail::TiledBufferInterfaceInterfaceTraits::FallbackModel<ConcreteOp>::getFullTileShape(const Concept *impl, ::mlir::Operation *tablegen_opaque_val) {
  return static_cast<const ConcreteOp *>(impl)->getFullTileShape(tablegen_opaque_val);
}
template<typename ConcreteOp>
llvm::ArrayRef<int64_t> detail::TiledBufferInterfaceInterfaceTraits::FallbackModel<ConcreteOp>::getStrides(const Concept *impl, ::mlir::Operation *tablegen_opaque_val) {
  return static_cast<const ConcreteOp *>(impl)->getStrides(tablegen_opaque_val);
}
} // namespace xla::xtile
