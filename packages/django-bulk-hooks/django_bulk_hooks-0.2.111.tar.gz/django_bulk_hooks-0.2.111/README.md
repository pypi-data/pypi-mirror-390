
# django-bulk-hooks

⚡ Bulk hooks for Django bulk operations and individual model lifecycle events.

`django-bulk-hooks` brings a declarative, hook-like experience to Django's `bulk_create`, `bulk_update`, and `bulk_delete` — including support for `BEFORE_` and `AFTER_` hooks, conditions, batching, and transactional safety. It also provides comprehensive lifecycle hooks for individual model operations.

## ✨ Features

- Declarative hook system: `@hook(AFTER_UPDATE, condition=...)`
- BEFORE/AFTER hooks for create, update, delete
- Hook-aware manager that wraps Django's `bulk_` operations
- **NEW**: `HookModelMixin` for individual model lifecycle events
- Hook chaining, hook deduplication, and atomicity
- Class-based hook handlers with DI support
- Support for both bulk and individual model operations

## 🚀 Quickstart

```bash
pip install django-bulk-hooks
```

### Define Your Model

```python
from django.db import models
from django_bulk_hooks.models import HookModelMixin

class Account(HookModelMixin):
    balance = models.DecimalField(max_digits=10, decimal_places=2)
    # The HookModelMixin automatically provides BulkHookManager
```

### Create a Hook Handler

```python
from django_bulk_hooks import hook, AFTER_UPDATE, Hook
from django_bulk_hooks.conditions import WhenFieldHasChanged
from .models import Account

class AccountHooks(Hook):
    @hook(AFTER_UPDATE, model=Account, condition=WhenFieldHasChanged("balance"))
    def log_balance_change(self, new_records, old_records):
        print("Accounts updated:", [a.pk for a in new_records])
    
    @hook(BEFORE_CREATE, model=Account)
    def before_create(self, new_records, old_records):
        for account in new_records:
            if account.balance < 0:
                raise ValueError("Account cannot have negative balance")
    
    @hook(AFTER_DELETE, model=Account)
    def after_delete(self, new_records, old_records):
        print("Accounts deleted:", [a.pk for a in old_records])
```

## 🛠 Supported Hook Events

- `BEFORE_CREATE`, `AFTER_CREATE`
- `BEFORE_UPDATE`, `AFTER_UPDATE`
- `BEFORE_DELETE`, `AFTER_DELETE`

## 🔄 Lifecycle Events

### Individual Model Operations

The `HookModelMixin` automatically hooks hooks for individual model operations:

```python
# These will hook BEFORE_CREATE and AFTER_CREATE hooks
account = Account.objects.create(balance=100.00)
account.save()  # for new instances

# These will hook BEFORE_UPDATE and AFTER_UPDATE hooks
account.balance = 200.00
account.save()  # for existing instances

# This will hook BEFORE_DELETE and AFTER_DELETE hooks
account.delete()
```

### Bulk Operations

Bulk operations also hook the same hooks:

```python
# Bulk create - hooks BEFORE_CREATE and AFTER_CREATE hooks
accounts = [
    Account(balance=100.00),
    Account(balance=200.00),
]
Account.objects.bulk_create(accounts)

# Bulk update - hooks BEFORE_UPDATE and AFTER_UPDATE hooks
for account in accounts:
    account.balance *= 1.1
Account.objects.bulk_update(accounts)  # fields are auto-detected

# Bulk delete - hooks BEFORE_DELETE and AFTER_DELETE hooks
Account.objects.bulk_delete(accounts)
```

### Queryset Operations

Queryset operations are also supported:

```python
# Queryset update - hooks BEFORE_UPDATE and AFTER_UPDATE hooks
Account.objects.update(balance=0.00)

# Queryset delete - hooks BEFORE_DELETE and AFTER_DELETE hooks
Account.objects.delete()
```

### Subquery Support in Updates

When using `Subquery` objects in update operations, the computed values are automatically available in hooks. The system efficiently refreshes all instances in bulk for optimal performance:

```python
from django.db.models import Subquery, OuterRef, Sum

def aggregate_revenue_by_ids(self, ids: Iterable[int]) -> int:
    return self.find_by_ids(ids).update(
        revenue=Subquery(
            FinancialTransaction.objects.filter(daily_financial_aggregate_id=OuterRef("pk"))
            .filter(is_revenue=True)
            .values("daily_financial_aggregate_id")
            .annotate(revenue_sum=Sum("amount"))
            .values("revenue_sum")[:1],
        ),
    )

# In your hooks, you can now access the computed revenue value:
class FinancialAggregateHooks(Hook):
    @hook(AFTER_UPDATE, model=DailyFinancialAggregate)
    def log_revenue_update(self, new_records, old_records):
        for new_record in new_records:
            # This will now contain the computed value, not the Subquery object
            print(f"Updated revenue: {new_record.revenue}")

# Bulk operations are optimized for performance:
def bulk_aggregate_revenue(self, ids: Iterable[int]) -> int:
    # This will efficiently refresh all instances in a single query
    return self.filter(id__in=ids).update(
        revenue=Subquery(
            FinancialTransaction.objects.filter(daily_financial_aggregate_id=OuterRef("pk"))
            .filter(is_revenue=True)
            .values("daily_financial_aggregate_id")
            .annotate(revenue_sum=Sum("amount"))
            .values("revenue_sum")[:1],
        ),
    )
```

## 🧠 Why?

Django's `bulk_` methods bypass signals and `save()`. This package fills that gap with:

- Hooks that behave consistently across creates/updates/deletes
- **NEW**: Individual model lifecycle hooks that work with `save()` and `delete()`
- Scalable performance via chunking (default 200)
- Support for `@hook` decorators and centralized hook classes
- **NEW**: Automatic hook hooking for admin operations and other Django features
- **NEW**: Proper ordering guarantees for old/new record pairing in hooks (Salesforce-like behavior)

## 📦 Usage Examples

### Individual Model Operations

```python
# These automatically hook hooks
account = Account.objects.create(balance=100.00)
account.balance = 200.00
account.save()
account.delete()
```

### Bulk Operations

```python
# These also hook hooks
Account.objects.bulk_create(accounts)
Account.objects.bulk_update(accounts)  # fields are auto-detected
Account.objects.bulk_delete(accounts)
```

### Advanced Hook Usage

```python
class AdvancedAccountHooks(Hook):
    @hook(BEFORE_UPDATE, model=Account, condition=WhenFieldHasChanged("balance"))
    def validate_balance_change(self, new_records, old_records):
        for new_account, old_account in zip(new_records, old_records):
            if new_account.balance < 0 and old_account.balance >= 0:
                raise ValueError("Cannot set negative balance")
    
    @hook(AFTER_CREATE, model=Account)
    def send_welcome_email(self, new_records, old_records):
        for account in new_records:
            # Send welcome email logic here
            pass
```

### Salesforce-like Ordering Guarantees

The system ensures that `old_records` and `new_records` are always properly paired, regardless of the order in which you pass objects to bulk operations:

```python
class LoanAccountHooks(Hook):
    @hook(BEFORE_UPDATE, model=LoanAccount)
    def validate_account_number(self, new_records, old_records):
        # old_records[i] always corresponds to new_records[i]
        for new_account, old_account in zip(new_records, old_records):
            if old_account.account_number != new_account.account_number:
                raise ValidationError("Account number cannot be changed")

# This works correctly even with reordered objects:
accounts = [account1, account2, account3]  # IDs: 1, 2, 3
reordered = [account3, account1, account2]  # IDs: 3, 1, 2

# The hook will still receive properly paired old/new records
LoanAccount.objects.bulk_update(reordered)  # fields are auto-detected
```

## 🧩 Integration with Other Managers

### Recommended: QuerySet-based Composition (New Approach)

For the best compatibility and to avoid inheritance conflicts, use the queryset-based composition approach:

```python
from django_bulk_hooks.queryset import HookQuerySet
from queryable_properties.managers import QueryablePropertiesManager

class MyManager(QueryablePropertiesManager):
    """Manager that combines queryable properties with hooks"""

    def get_queryset(self):
        # Get the QueryableProperties QuerySet
        qs = super().get_queryset()
        # Apply hooks on top of it
        return HookQuerySet.with_hooks(qs)

class Article(models.Model):
    title = models.CharField(max_length=100)
    published = models.BooleanField(default=False)

    objects = MyManager()

# This gives you both queryable properties AND hooks
# No inheritance conflicts, no MRO issues!
```

### Alternative: Explicit Hook Application

For more control, you can apply hooks explicitly:

```python
class MyManager(QueryablePropertiesManager):
    def get_queryset(self):
        return super().get_queryset()

    def with_hooks(self):
        """Apply hooks to this queryset"""
        return HookQuerySet.with_hooks(self.get_queryset())

# Usage:
Article.objects.with_hooks().filter(published=True).update(title="Updated")
```

### Legacy: Manager Inheritance (Not Recommended)

The old inheritance approach still works but is not recommended due to potential MRO conflicts:

```python
from django_bulk_hooks.manager import BulkHookManager
from queryable_properties.managers import QueryablePropertiesManager

class MyManager(BulkHookManager, QueryablePropertiesManager):
    pass  # ⚠️ Can cause inheritance conflicts
```

**Why the new approach is better:**
- ✅ No inheritance conflicts
- ✅ No MRO (Method Resolution Order) issues
- ✅ Works with any manager combination
- ✅ Cleaner and more maintainable
- ✅ Follows Django's queryset enhancement patterns

Framework needs to:
Register these methods
Know when to execute them (BEFORE_UPDATE, AFTER_UPDATE)
Execute them in priority order
Pass ChangeSet to them
Handle errors (rollback on failure)

## 📝 License

MIT © 2024 Augend / Konrad Beck
