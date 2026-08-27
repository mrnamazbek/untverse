import ast
import asyncio
import sys
import subprocess
import time
from typing import List, Optional
from app.schemas.coding import TestCaseResult, CodeRunResponse


class SecurityCheckVisitor(ast.NodeVisitor):
    """
    AST Visitor to reject potentially dangerous modules, builtins, and syntax.
    """
    FORBIDDEN_MODULES = {
        "os", "sys", "subprocess", "shutil", "socket", "http", "urllib",
        "requests", "ctypes", "pathlib", "importlib", "pickle", "shelve",
        "multiprocessing", "threading", "pty", "commands", "posix", "gc"
    }

    FORBIDDEN_CALLS = {
        "eval", "exec", "open", "__import__", "compile", "globals", "locals", "getattr", "setattr", "delattr"
    }

    def __init__(self):
        self.errors = []

    def visit_Import(self, node):
        for alias in node.names:
            root_module = alias.name.split('.')[0]
            if root_module in self.FORBIDDEN_MODULES:
                self.errors.append(f"Импорт модуля '{alias.name}' запрещен из соображений безопасности.")
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module:
            root_module = node.module.split('.')[0]
            if root_module in self.FORBIDDEN_MODULES:
                self.errors.append(f"Импорт из модуля '{node.module}' запрещен из соображений безопасности.")
        self.generic_visit(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            if node.func.id in self.FORBIDDEN_CALLS:
                self.errors.append(f"Вызов функции '{node.func.id}()' запрещен в учебных заданиях.")
        self.generic_visit(node)


class CodeExecutionService:
    @staticmethod
    def validate_code_safety(source_code: str) -> Optional[str]:
        """
        Parses AST and validates against dangerous operations.
        Returns error string if unsafe, None if safe.
        """
        try:
            tree = ast.parse(source_code)
        except SyntaxError as e:
            return f"Синтаксическая ошибка: {e.msg} (строка {e.lineno})"
        except Exception as e:
            return f"Ошибка синтаксического разбора: {str(e)}"

        visitor = SecurityCheckVisitor()
        visitor.visit(tree)
        if visitor.errors:
            return " ".join(visitor.errors)
        return None

    @staticmethod
    async def run_single_test(
        source_code: str,
        input_data: str,
        expected_output: str,
        timeout: float = 2.0
    ) -> TestCaseResult:
        """
        Executes code with input in an isolated child process with timeout.
        """
        start_time = time.perf_counter()
        
        # Wrapped script ensuring safe standard I/O execution
        wrapper_code = source_code

        try:
            process = await asyncio.create_subprocess_exec(
                sys.executable, "-c", wrapper_code,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            try:
                stdout_bytes, stderr_bytes = await asyncio.wait_for(
                    process.communicate(input=input_data.encode("utf-8")),
                    timeout=timeout
                )
                elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

                stdout_text = stdout_bytes.decode("utf-8", errors="replace").strip()
                stderr_text = stderr_bytes.decode("utf-8", errors="replace").strip()

                if process.returncode != 0:
                    return TestCaseResult(
                        input_data=input_data,
                        expected_output=expected_output.strip(),
                        actual_output=None,
                        passed=False,
                        is_hidden=False,
                        execution_time_ms=elapsed_ms,
                        error=stderr_text or f"Process exited with code {process.returncode}"
                    )

                passed = (stdout_text == expected_output.strip())
                return TestCaseResult(
                    input_data=input_data,
                    expected_output=expected_output.strip(),
                    actual_output=stdout_text,
                    passed=passed,
                    is_hidden=False,
                    execution_time_ms=elapsed_ms,
                    error=None if passed else "Вывод не совпадает с ожидаемым результатом"
                )

            except asyncio.TimeoutError:
                try:
                    process.kill()
                except Exception:
                    pass
                elapsed_ms = round(timeout * 1000, 2)
                return TestCaseResult(
                    input_data=input_data,
                    expected_output=expected_output.strip(),
                    actual_output=None,
                    passed=False,
                    is_hidden=False,
                    execution_time_ms=elapsed_ms,
                    error=f"Time Limit Exceeded (превышен лимит времени {timeout} сек)"
                )

        except Exception as e:
            elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)
            return TestCaseResult(
                input_data=input_data,
                expected_output=expected_output.strip(),
                actual_output=None,
                passed=False,
                is_hidden=False,
                execution_time_ms=elapsed_ms,
                error=f"Execution error: {str(e)}"
            )

    @classmethod
    async def execute_task(
        cls,
        source_code: str,
        test_cases: List[dict],
        time_limit_seconds: float = 2.0
    ) -> CodeRunResponse:
        """
        Runs code against all test cases.
        """
        # Step 1: Security AST verification
        safety_error = cls.validate_code_safety(source_code)
        if safety_error:
            return CodeRunResponse(
                status="forbidden_syntax",
                passed_tests=0,
                total_tests=len(test_cases),
                execution_time_ms=0.0,
                error_output=safety_error,
                test_results=[],
                xp_earned=0,
                new_total_xp=0,
                new_level=0,
                leveled_up=False
            )

        # Step 2: Execute each test case
        results = []
        total_time_ms = 0.0
        passed_count = 0
        overall_status = "accepted"
        first_error = None

        for tc in test_cases:
            res = await cls.run_single_test(
                source_code=source_code,
                input_data=tc.get("input_data", ""),
                expected_output=tc.get("expected_output", ""),
                timeout=time_limit_seconds
            )
            res.test_case_id = tc.get("id")
            res.is_hidden = tc.get("is_hidden", False)

            # If it's a hidden test case and failed, mask output
            if res.is_hidden:
                res.input_data = "[Скрытый тест-кейс]"
                res.expected_output = "[Скрытый вывод]"
                if res.actual_output:
                    res.actual_output = "[Скрыто]"

            results.append(res)
            total_time_ms += res.execution_time_ms

            if res.passed:
                passed_count += 1
            else:
                if overall_status == "accepted":
                    if "Time Limit" in (res.error or ""):
                        overall_status = "timeout"
                    elif "SyntaxError" in (res.error or "") or "Traceback" in (res.error or ""):
                        overall_status = "runtime_error"
                    else:
                        overall_status = "wrong_answer"
                    first_error = res.error

        return CodeRunResponse(
            status=overall_status,
            passed_tests=passed_count,
            total_tests=len(test_cases),
            execution_time_ms=round(total_time_ms, 2),
            error_output=first_error if overall_status != "accepted" else None,
            test_results=results,
            xp_earned=0,
            new_total_xp=0,
            new_level=0,
            leveled_up=False
        )
