#include "llvm/Pass.h"
#include "llvm/IR/Function.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/IR/LegacyPassManager.h"
#include "llvm/Transforms/IPO/PassManagerBuilder.h"
#include "llvm/MC/MCInstPrinter.h"
#include "llvm/MC/MCInstrInfo.h"
#include "llvm/MC/MCRegisterInfo.h"
#include "llvm/MC/MCSubtargetInfo.h"
#include "llvm/MC/MCAsmInfo.h"
#include "llvm/MC/MCContext.h"
#include "llvm/CodeGen/TargetSubtargetInfo.h"
#include "llvm/Target/TargetMachine.h"
#include "llvm/Support/TargetRegistry.h"
#include "llvm/Support/Host.h"
#include "llvm/Support/TargetRegistry.h"
#include <vector>

using namespace llvm;

namespace {

struct PrintBB : public FunctionPass {
  static char ID;
  PrintBB() : FunctionPass(ID) {}

  bool runOnFunction(Function &F) override {
    errs() << "Printing assembly of function: " << F.getName() << "\n";
    const Target *TheTarget = TargetRegistry::lookupTarget(MArch, TheTriple, error);
    if (!TheTarget) {
      errs() << "Cannot find target\n";
      return false;
    }

    std::unique_ptr<MCSubtargetInfo> STI(TheTarget->createMCSubtargetInfo(TheTriple.str(), "", ""));
    std::unique_ptr<MCInstrInfo> MII(TheTarget->createMCInstrInfo());
    std::unique_ptr<MCRegisterInfo> MRI(TheTarget->createMCRegInfo(TheTriple.str()));
    std::unique_ptr<MCAsmInfo> MAI(TheTarget->createMCAsmInfo(*MRI, TheTriple.str()));

    MCContext Ctx(MAI.get(), MRI.get(), nullptr);
    std::unique_ptr<MCInstPrinter> IP(TheTarget->createMCInstPrinter(Triple(TripleName), 0, *MAI, *MII, *MRI));
    IP->setPrintBranchImmAsAddress(true);

    for(Function::iterator BI = F.begin(), BE = F.end(); BI != BE; ++BI) {
      errs() << IP->getOpcodeName(BI->getTerminator()->getOpcode()) << "\n";
      for(BasicBlock::iterator II = BI->begin(), IE = BI->end(); II != IE; ++II) {
        if (!II->isMetaInstruction()) {
          IP->printInst(&*II, Ctx, errs());
          errs() << "\n";
        }
      }
    }

    return false;
  }

  std::string MArch = "native";
  std::string TripleName = sys::getDefaultTargetTriple();
  Triple TheTriple = new Triple();
  // TheTriple.normalize(TripleName);
  std::string error;
};

} // end anonymous namespace

char PrintBB::ID = 0;

static RegisterPass<PrintBB> X("print-bb", "Print Assembly Code of Basic Blocks in Function");