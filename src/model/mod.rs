use std::ops::{Deref, DerefMut};

pub mod event;
pub mod journal;

type Tx<'c> = sqlx::Transaction<'c, sqlx::Sqlite>;

pub struct Session<'c>(pub Tx<'c>);

impl<'c> Session<'c> {
    #[allow(unused)]
    pub async fn commit(self) -> anyhow::Result<()> {
        self.0.commit().await.map_err(|e| e.into())
    }

    #[allow(unused)]
    pub async fn rollback(self) -> anyhow::Result<()> {
        self.0.rollback().await.map_err(|e| e.into())
    }
}

impl<'c> Deref for Session<'c> {
    type Target = Tx<'c>;
    fn deref(&self) -> &Self::Target {
        &self.0
    }
}

impl<'c> DerefMut for Session<'c> {
    fn deref_mut(&mut self) -> &mut Self::Target {
        &mut self.0
    }
}

impl<'c> AsRef<Tx<'c>> for Session<'c> {
    fn as_ref(&self) -> &Tx<'c> {
        &self.0
    }
}

impl<'c> AsMut<Tx<'c>> for Session<'c> {
    fn as_mut(&mut self) -> &mut Tx<'c> {
        &mut self.0
    }
}
