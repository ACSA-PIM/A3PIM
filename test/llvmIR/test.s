	.text
	.file	"test.cpp"
	.globl	main                    # -- Begin function main
	.p2align	4, 0x90
	.type	main,@function
main:                                   # @main
	.cfi_startproc
# %bb.0:
	pushq	%rbx
	.cfi_def_cfa_offset 16
	.cfi_offset %rbx, -16
	movl	$_ZSt4cout, %edi
	movl	$.L.str, %esi
	movl	$13, %edx
	callq	_ZSt16__ostream_insertIcSt11char_traitsIcEERSt13basic_ostreamIT_T0_ES6_PKS3_l
	movq	_ZSt4cout(%rip), %rax
	movq	-24(%rax), %rax
	movq	_ZSt4cout+240(%rax), %rbx
	testq	%rbx, %rbx
	je	.LBB0_5
# %bb.1:
	cmpb	$0, 56(%rbx)
	je	.LBB0_3
# %bb.2:
	movb	67(%rbx), %al
	jmp	.LBB0_4
.LBB0_3:
	movq	%rbx, %rdi
	callq	_ZNKSt5ctypeIcE13_M_widen_initEv
	movq	(%rbx), %rax
	movq	%rbx, %rdi
	movl	$10, %esi
	callq	*48(%rax)
.LBB0_4:
	movsbl	%al, %esi
	movl	$_ZSt4cout, %edi
	callq	_ZNSo3putEc
	movq	%rax, %rdi
	callq	_ZNSo5flushEv
	xorl	%eax, %eax
	popq	%rbx
	.cfi_def_cfa_offset 8
	retq
.LBB0_5:
	.cfi_def_cfa_offset 16
	callq	_ZSt16__throw_bad_castv
.Lfunc_end0:
	.size	main, .Lfunc_end0-main
	.cfi_endproc
                                        # -- End function
	.section	.text.startup,"ax",@progbits
	.p2align	4, 0x90         # -- Begin function _GLOBAL__sub_I_test.cpp
	.type	_GLOBAL__sub_I_test.cpp,@function
_GLOBAL__sub_I_test.cpp:                # @_GLOBAL__sub_I_test.cpp
	.cfi_startproc
# %bb.0:
	pushq	%rax
	.cfi_def_cfa_offset 16
	movl	$_ZStL8__ioinit, %edi
	callq	_ZNSt8ios_base4InitC1Ev
	movl	$_ZNSt8ios_base4InitD1Ev, %edi
	movl	$_ZStL8__ioinit, %esi
	movl	$__dso_handle, %edx
	popq	%rax
	.cfi_def_cfa_offset 8
	jmp	__cxa_atexit            # TAILCALL
.Lfunc_end1:
	.size	_GLOBAL__sub_I_test.cpp, .Lfunc_end1-_GLOBAL__sub_I_test.cpp
	.cfi_endproc
                                        # -- End function
	.type	_ZStL8__ioinit,@object  # @_ZStL8__ioinit
	.local	_ZStL8__ioinit
	.comm	_ZStL8__ioinit,1,1
	.hidden	__dso_handle
	.type	.L.str,@object          # @.str
	.section	.rodata.str1.1,"aMS",@progbits,1
.L.str:
	.asciz	"Hello, world!"
	.size	.L.str, 14

	.section	.init_array,"aw",@init_array
	.p2align	3
	.quad	_GLOBAL__sub_I_test.cpp
	.ident	"clang version 10.0.0-4ubuntu1 "
	.section	".note.GNU-stack","",@progbits
